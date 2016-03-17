import os
import threading
import time


class ProgressTree(threading.Thread):
    def __init__(self, indent=2):
        super().__init__()
        self.is_running = True
        self.depth2pbar = dict()
        self.indent = indent
        self.current_depth = 0

    def run(self):
        while self.is_running:
            self.draw()
        for _, pbar in sorted(self.depth2pbar.items()):
            print(pbar.get_text(pbar.max_value))

    def draw(self):
        time.sleep(0.05)
        for i in range(self.current_depth + 1):
            self.depth2pbar[i].draw()

    def __call__(self, depth, max_value, text='Progress'):
        assert depth > 0, 'depth should be over 1'
        # reuse
        if depth in self.depth2pbar:
            pbar = self.depth2pbar[depth]
        else:
            # root
            if depth == 0:
                pbar = ProgressBar(max_value, depth, 0, self.indent, text)
            # new
            elif self.depth2pbar[depth - 1].is_finished:
                nest = self.depth2pbar[depth - 1].depth + 1
                pbar = ProgressBar(max_value, depth, nest, self.indent, text)
            self.depth2pbar[depth] = pbar
        self.current_depth = depth
        return pbar

    def finish(self):
        self.is_running = False


class ProgressBar:
    def __init__(self, max_value, depth, nest, indent, text):
        self.value = 0
        self.max_value = max_value
        self.depth = depth
        self.nest = nest
        self.indent = indent
        self.text = text
        self.is_finished = False

    def __call__(self, iterable):
        for i, item in enumerate(iterable):
            self.value += 1
            yield item
        self.is_finished = True

    def draw(self):
        for _ in range(self.depth):
            print('')
        print(self.get_text(), end='', flush=True)
        for _ in range(self.depth):
            print('\x1b[1A', end='')

    def get_text(self, value=None):
        value = self.value if value is None else value
        indent = ' ' * (self.nest * self.indent)
        header = '\r' + indent
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

# 全体に一つでもbranchがある場合は、一番高いbranchの最後が消えるときに、対象以下をすべて消す
# ある位置より上にbranchがなければ、（そのまま上に戻るだけなら）ある位置より以下をすべて消す
# new するときにわかる？前のdepthをとっておく必要がある？
# new するときに削除の操作を担う

t = ProgressTree()
t.start()
for _ in t(1, 2, 'P1')(range(2)):
    for _ in t(2, 3, 'P2')(range(3)):
        for _ in t(3, 4, 'P4')(range(4)):
            time.sleep(0.1)
#for _ in t(1, 2, '1')(range(2)):
#    for _ in t(2, 3, '2')(range(3)):
#        for _ in t(3, 6, '3')(range(6)):
#            time.sleep(0.1)
#        for _ in t(3, 6, '4')(range(6)):
#            for _ in t(4, 6, '5')(range(6)):
#                time.sleep(0.1)
#        for _ in t(3, 6, '6')(range(6)):
#            time.sleep(0.1)
t.finish()
