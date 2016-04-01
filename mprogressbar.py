import os
import sys
import time
from multiprocessing import Process, Manager, Value


class ProgressManager:
    def __init__(self, target=sys.stdout, width=None):
        m = Manager()
        self.order2text = m.dict()
        self.is_running = Value('i', 1)
        self.p = Process(target=self.draw, args=(target,))
        if width is None:
            width = get_col()
        self.width = width

    def draw(self, target):
        cuu1 = '\x1b[A'
        dl1 = '\x1b[M'
        upnum = 0
        sp = target.tell()
        while self.is_running.value == 1:
            text = '\n'.join(item[1] for item in sorted(self.order2text.items(), key=lambda x:x[0]))
            if target != sys.stdout:
                target.seek(sp)
            else:
                print(cuu1 * upnum, end='')
                upnum = text.count('\n') + 1
            print(text, flush=True, file=target)

    def new_tree(self, offset=None):
        if offset is None:
            if len(self.order2text) == 0:
                offset = 0
            else:
                offset = len(self.order2text)
        return ProgressTree(self.order2text, self.width, offset=offset)

    def start(self):
        self.p.start()

    def finish(self):
        time.sleep(0.5)
        self.is_running.value = 0
        self.p.join()


class ProgressTree:
    def __init__(self, order2text, width, indent=3, offset=0):
        self.indent = indent
        self.offset = offset
        self.order2text = order2text
        self.order2pbar = dict()
        self.cursor = '-->'
        self.non_cursor = '   '
        self.width = width

    def __call__(self, text, maxv, order, nest):
        assert order > 0, 'order should be over 1'
        order -= 1
        order += self.offset
        text = text.replace('\n', ' ')

        # reuse
        if order in self.order2pbar:
            pbar = self.order2pbar[order]
            pbar.value = 0
        else:
            pbar = ProgressBar(maxv, order, nest, self.indent, text, self.update, self.order2text, self.width)
            self.order2pbar[order] = pbar
        return pbar

    def print(self, text, order, nest, fill=' '):
        order -= 1
        order += self.offset
        if text != '':
            text = text.replace('\n', ' ')
            text = self.non_cursor + ' ' * self.indent * nest + text
        remlen = self.width - len(text)
        text += fill * remlen

        self.order2text[order] = text

    def update(self, pbar):
        for p in self.order2pbar.values():
            p.cursor = self.non_cursor
            self.order2text[p.order] = p.get_text()
        pbar.cursor = self.cursor

    def finish(self):
        self.is_running.value = 0
        self.drawp.join()


class ProgressBar:
    def __init__(self, max_value, order, nest, indent, text, update, order2text, width):
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
        self.width = width

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
        #header = '\r' + self.cursor + indent
        header = self.cursor + indent
        per = value / self.max_value
        length = len(str(self.max_value))
        template = '{{}}: {{:0>{length}}}/{{}}: {{:.1f}}%|'.format(length=length).format(self.text, value, self.max_value, per * 100)
        text = header + template
        remlen = self.width - len(text) - 2
        proglen = int(remlen * per)
        bar = '[{}{}]'.format('#' * proglen, ' ' * (remlen - proglen))
        text += bar
        return text


def get_col():
    return os.get_terminal_size().columns
