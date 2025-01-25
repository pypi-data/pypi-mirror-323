from abc import ABC, abstractmethod


class Processor(ABC):
    r'''
    function to handle a single data
    return None if no data needs to return. Otherwise, return a list of transformed data
    It is useful when certain filtering logic is needed
    '''
    @abstractmethod
    def transform(self, item, is_last_sample=False):
        pass

    r'''
    function to handle a batch of data
    input:
        list_of_items -- data to be batch processed
        is_last_batch -- whether current batch is the last batch might be useful if the last batch's 
                         tranform logic is different from the normal batches.
    return:
        the transformed batch data. None if no data needs to return, otherwise, it should be a list of batch data
        since buffer gathering logic might exist, and it is possible to return multiple of batch data.
    '''
    @abstractmethod
    def batch_transform(self, list_of_items, is_last_batch=False):
        pass


class AncProcessor(Processor):
    r'''
    A processor that does nothing but return the input as is for both transform and batch transform function
    '''
    def transform(self, item, is_last_sample=False):
        return [item]

    # we wrap out data to a list to follow the return pattern in the base class
    def batch_transform(self, list_of_items, is_last_batch=False):
        return [list_of_items]


# AncComposerBuffer uses get_token_length_fn to get the token length of each sample.
# Set get_token_length_fn properly to make sample composing correct.
class AncComposerBuffer:
    def __init__(self, get_token_length_fn=None):
        self.buffer = []
        self.total_token_length = 0
        if get_token_length_fn is None:
            self.get_token_length_fn = lambda x: 1
        else:
            self.get_token_length_fn = get_token_length_fn
        self.delete_idx = set()
        self.cur_idx = 0

    def put(self, item):
        if item is not None:
            token_length = self.get_token_length_fn(item)
            self.buffer.append((token_length, item))
            self.total_token_length += token_length
        return self.total_token_length

    # return the first sample whose token length is smaller than the target length
    def get(self, target_length):
        for i in range(len(self.buffer)):
            idx = (i + self.cur_idx) % len(self.buffer)
            if idx in self.delete_idx:
                continue
            if self.buffer[idx][0] <= target_length:
                self.delete_idx.add(idx)
                self.total_token_length -= self.buffer[idx][0]
                self.cur_idx = (idx + 1) % len(self.buffer)
                return self.buffer[idx]
        return None
    
    def get_all(self):
        res = self.buffer
        self.buffer = []
        self.total_token_length = 0
        self.delete_idx = set()
        self.cur_ids = 0
        return res

    def flush(self):
        buffer = [self.buffer[i] for i in range(len(self.buffer)) if i not in self.delete_idx]
        self.buffer = buffer
        self.delete_idx = set()


class AncComposer:
    def __init__(self, max_seq_len, get_token_length_fn=None, ratio=2.0):
        self.max_seq_len = max_seq_len
        self.buffer = AncComposerBuffer(get_token_length_fn)
        # ratio here controls how many samples would be collected in the buffer
        # it might be difficult to compose enough samples to reach the max_seq_len when buffer size is small
        self.ratio = ratio

    def get_items(self, is_last_call=False):
        items = []
        if is_last_call:
            items = self.buffer.get_all()
            items = [i[1] for i in items if i is not None]
            return items
        cur_seq_length = self.max_seq_len
        while True:
            item = self.buffer.get(cur_seq_length)
            if item is None:
                break
            assert len(item) == 2
            items.append(item[1])
            cur_seq_length = cur_seq_length - item[0]
            if cur_seq_length == 0:
                break
        self.buffer.flush()
        return items

    def apply(self, sample, is_last_call=False):
        total_token_length = self.buffer.put(sample)
        res = []
        if total_token_length >= self.max_seq_len * self.ratio:
            items = self.get_items()
            res.append(items)
        if is_last_call:
            while total_token_length >= self.max_seq_len:
                items = self.get_items()
                res.append(items)
                total_token_length = self.buffer.put(None)
            if total_token_length > 0:
                items = self.get_items(is_last_call=True)
                res.append(items)
        return res if len(res) > 0 else None
    
    def __call__(self, samples, is_last_call=False):
        for sample in samples:
            res = self.apply(sample)
            if res is None:
                continue
            yield from res
        if is_last_call:
            res = self.apply(None, True)
            if res is not None:
                yield from res
