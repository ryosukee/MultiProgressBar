import os
import time
from multiprocessing import Process, Manager, Value


class ProgressManager:
    def __init__(self):
        m = Manager()
        self.order2text = m.dict()
        self.is_running = Value('i', 1)
        self.p = Process(target=self.draw)
        self.p.start()

    def draw(self):
        order2maxtext = dict()
        while self.is_running.value == 1:
            for order, text in self.order2text.items():
                order2maxtext[order] = text
                text = '\n' * order + text + '\x1b[1A' * order
                print(text, end='', flush=True)
            time.sleep(0.05)
        for i in range(max(order2maxtext) + 1):
            if i not in order2maxtext:
                print('', flush=True)
            else:
                print(order2maxtext[i], flush=True)

    def new_tree(self, offset=None):
        if offset is None:
            if len(self.order2text) == 0:
                offset = 0
            else:
                offset = len(self.order2text)
        return ProgressTree(self.order2text, offset=offset)

    def finish(self):
        self.is_running.value = 0


class ProgressTree:
    def __init__(self, order2text, indent=3, offset=0):
        self.indent = indent
        self.offset = offset
        self.order2text = order2text
        self.order2pbar = dict()

    def add(self, text, order, maxv, nest):
        assert order > 0, 'order should be over 1'
        order -= 1
        order += self.offset

        # reuse
        if order in self.order2pbar:
            pbar = self.order2pbar[order]
            pbar.value = 0
        else:
            pbar = ProgressBar(maxv, order, nest, self.indent, text, self.update, self.order2text)
            self.order2pbar[order] = pbar
        return pbar

    def update(self, pbar):
        for p in self.order2pbar.values():
            p.cursor = '   '
            self.order2text[p.order] = p.get_text()
        pbar.cursor = '-->'

    def finish(self):
        self.is_running.value = 0
        self.drawp.join()


class ProgressBar:
    def __init__(self, max_value, order, nest, indent, text, update, order2text):
        self.value = 0
        self.max_value = max_value
        self.order = order
        self.nest = nest
        self.indent = indent
        self.text = text
        self.is_finished = False
        self.color = ''
        self.cursor = '   '
        self.update = update
        self.order2text = order2text

    def __call__(self, iterable):
        self.update(self)
        for i, item in enumerate(iterable):
            self.value += 1
            self.order2text[self.order] = self.get_text()
            yield item
        self.is_finished = True

    def get_text(self, value=None):
        value = self.value if value is None else value
        indent = ' ' * (self.nest * self.indent)
        header = '\r' + self.cursor + indent
        per = value / self.max_value
        length = len(str(self.max_value))
        template = '{{}}: {{:0>{length}}}/{{}}: {{:.2f}}|'.format(length=length).format(self.text, value, self.max_value, per * 100)
        text = header + template
        remlen = self.get_col() - len(text) - 2
        proglen = int(remlen * per)
        bar = '[{}{}]'.format('#' * proglen, ' ' * (remlen - proglen))
        text += bar
        return text

    def get_col(self):
        return os.get_terminal_size().columns
