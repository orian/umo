# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

a='51.01 633.55 Td\n'
b='(LICZBA UPRAWNIONYCH) Tj\n'
re.compile(r'() () Td\\n')
m = re.match(r'(?P<x>[\d\.]+) (?P<y>[\d\.]+) Td\n', a)
print(m.groupdict())
t = re.match(r'\((?P<t>.*)\) Tj\n', b)
print(t.groupdict())

# <codecell>

import json
import re

DEBUG=False

# here it starts
class Context(object):
    def __init__(self):
        self._stack = []
        self._start_state = State('start')
        self._end_state = State('end')
        self._state = self._start_state
        self._texts = []
    def run(self, f):
        line_counter = 0
        for line in f:
            follow = True
            while follow:
                x, follow = self._state.update(self, line)
                if x != None:
                    self._state.on_exit(self)
                    self._state = x
                    self._state.on_enter(self)

                if self._state == self._end_state:
                    return
                line_counter+=1
#                 if line_counter > 400:
#                     return


class State(object):
    def __init__(self, name):
        self._name = name
        self._transition_func_and_state = []
    def add_state(self, func, state, follow=False):
        self._transition_func_and_state.append((func, state, follow,))
    def update(self, ctx, text):
#         print('got line: {}'.format(text))
        for func,state,follow in self._transition_func_and_state:
            if func(text):
                return state,follow
        return None,False
    def on_exit(self, ctx):
        if DEBUG:
            print('on_exit: {}'.format(self._name))
    def on_enter(self, ctx):
        if DEBUG:
            print('on_enter: {}'.format(self._name))


class TextObj(object):
    def __init__(self):
        self._x = 0.0
        self._y = 0.0
        self._text = ''
    def __str__(self):
        return '({x} {y} \'{t}\')'.format(x=self._x, y=self._y, t=self._text)
    def __unicode__(self):
        return '({x} {y} \'{t}\')'.format(x=self._x, y=self._y, t=self._text)
    def __repr__(self):
        return '({x} {y} \'{t}\')'.format(x=self._x, y=self._y, t=self._text)


class BoxStateStart(State):
    def on_enter(self, ctx):
        ctx._texts.append(('MARKER',))
        super(BoxStateStart, self).on_enter(ctx)

class BoxStateEnd(State):
    def on_exit(self, ctx):
        stack=[]
        idx = 1
        for a in reversed(ctx._texts):
#             print(a)
            if type(a) is tuple and a[0]=='MARKER':
#                 print ('breaking {}'.format(idx))
                break
            stack.append(a)
            idx+=1
        ctx._texts = ctx._texts[:-idx]
        if idx>1:
            t = []
            for x in reversed(stack):
                t.append(x._text)

            stack[-1]._text = ' '.join(t)
#             print('joined from {} {} {}'.format(idx, len(t), stack[-1]._text))
            ctx._texts.append(stack[-1])
        super(BoxStateEnd, self).on_exit(ctx)


'51.01 633.55 Td\n'
'(LICZBA UPRAWNIONYCH) Tj\n'
class TextState(State):
    def __init__(self, name):
        super(TextState, self).__init__(name)
    def reset(self):
        self._text = TextObj()
        self._has_text = False
        self._has_xy = False
    def update(self, ctx, text):
        m = re.match(r'(?P<x>[\d\.]+) (?P<y>[\d\.]+) Td\n', text)
        if m != None:
            if DEBUG:
                print('x y match')
            m = m.groupdict()
            self._text._x = m['x']
            self._text._y = m['y']
            self._has_xy = True
        else:
            t = re.match(r'\((?P<t>.*)\) Tj\n', text)
            if t != None:
                if DEBUG:
                    print('title match')
                t = t.groupdict()
                self._text._text = t['t']
                self._has_text = True
        return super(TextState, self).update(ctx, text)
    def on_enter(self, ctx):
        if DEBUG:
            print('on_enter: {}'.format(self._name))
        self.reset()
    def on_exit(self, ctx):
        if DEBUG:
            print('parsed: {}'.format(self._text.__unicode__()))
        ctx._texts.append(self._text)
        self._text = None

def create_state_machine(f):
    ctx = Context()
    s_obj = State('obj')
    obj_start_f = lambda t: t.find('obj\n') >=0
    obj_end_f = lambda t: t.find('endobj\n') >=0

    ctx._start_state.add_state(obj_start_f, s_obj)
    s_obj.add_state(obj_end_f, ctx._start_state)

    s_stream = State('stream')
    stream_start_f = lambda t: t.find('stream\n') >=0
    stream_end_f = lambda t: t.find('endstream\n') >=0

    s_obj.add_state(stream_start_f, s_stream)
    s_stream.add_state(stream_end_f, s_obj)

    s_text = TextState('text')
    text_start_f = lambda t: t.find('BT\n') >=0
    text_end_f = lambda t: t.find('ET\n') >=0

    s_stream.add_state(text_start_f, s_text)
    s_text.add_state(text_end_f, s_stream)

    ctx.run(f)
    return ctx._texts

def create_state_machine2(f):
    ctx = Context()
    s_obj = State('obj')
    obj_start_f = lambda t: t.find('obj\n') >=0
    obj_end_f = lambda t: t.find('endobj\n') >=0

    ctx._start_state.add_state(obj_start_f, s_obj)
    s_obj.add_state(obj_end_f, ctx._start_state)

    s_stream = State('stream')
    stream_start_f = lambda t: t.find('stream\n') >=0
    stream_end_f = lambda t: t.find('endstream\n') >=0

    s_obj.add_state(stream_start_f, s_stream)
    s_stream.add_state(stream_end_f, s_obj)

    s_box = BoxStateStart('box_start')
    box_start_f = lambda t: t=='n\n'
    box_end_f = lambda t: t=='W\n'
    s_stream.add_state(box_start_f, s_box, follow=True)

    s_box_wait = State('box_wait')
    s_box.add_state(lambda x:True, s_box_wait)
    # there may be 2 ways to end box
    s_box_end = BoxStateEnd('box_end')
    s_box_wait.add_state(box_end_f, s_box_end, follow=True)
    s_box_wait.add_state(stream_end_f, s_box_end, follow=True)
    s_box_end.add_state(lambda x:True, s_stream, follow=True)

    s_text = TextState('text')
    text_start_f = lambda t: t.find('BT\n') >=0
    text_end_f = lambda t: t.find('ET\n') >=0

    s_box_wait.add_state(text_start_f, s_text)
    s_text.add_state(text_end_f, s_box_wait)

    ctx.run(f)
    return ctx._texts

# <codecell>

from operator import itemgetter, attrgetter

class Parser(object):
    def __init__(self, t_list):
        s = sorted(t_list, key=lambda x: float(x._x))
        self._text_objs = sorted(s, key=lambda x: float(x._y), reverse=True)
        self._idx = 0
        self._data = {'votes':[]}
        self._prev = None
        self._d_x = 2.0
        self._d_y = 2.0
    def __str__(self):
        return self._data.__str__()

    def fill(self, move_x, move_y, field, obj=None, parser=None):
        assert move_x == 0 or move_y == 0

        curr = self._text_objs[self._idx]
        prev = self._prev
        if self._prev:
            if move_x>0:
                assert float(curr._x) >= float(prev._x)+self._d_x, "{} is NOT more to right than {}".format(curr, prev)
            if move_y>0:
                assert float(curr._y) <= float(prev._y)-self._d_y, "{} is NOT lower than {}".format(curr, prev)
        val = curr._text
        if parser != None:
            val = parser(val)
        if obj != None:
            obj[field] = val
        else:
            self._data[field] = val
        self._prev = curr
        self._idx += 1

    def maybe_fill(self, move_x, move_y, field, cond=None, obj=None, parser=None):
        assert move_x == 0 or move_y == 0

        if self._idx >= len(self._text_objs):
            return False
        curr = self._text_objs[self._idx]
        prev = self._prev

        if cond != None and not cond(curr._text):
            return False

        r_val = True
        if self._prev:
            if move_x>0:
                r_val = float(curr._x) >= float(prev._x)+self._d_x
            if move_y>0:
                r_val = float(curr._y) <= float(prev._y)-self._d_y

        self._prev = curr
        self._idx += 1
        if not r_val:
            return False

        val = curr._text
        if parser != None:
            try:
                val = parser(val)
            except:
                return False
        if obj != None:
            obj[field] = val
        else:
            self._data[field] = val

        return True

    def skip(self, move_x, move_y):
        assert move_x == 0 or move_y == 0

        self._prev = self._text_objs[self._idx]
        self._idx += move_x+move_y

    def maybe_skip(self, move_x, move_y, cond=None):
        assert move_x == 0 or move_y == 0

        if self._idx >= len(self._text_objs):
            return False

        curr = self._text_objs[self._idx]

        if cond != None and not cond(curr._text):
            return False

        self._prev = curr
        self._idx += 1
        return True

    def rewind(self, d_idx):
        self._idx += d_idx
        if self._idx>0:
            self._prev = self._text_objs[self._idx-1]
        else:
            self._prev = None

    def parse(self):
        self.fill(0,0,'council_session')
        self.skip(0,1)
        # number and title, they are in one row
        self.fill(0,1,'number')
        if not self.maybe_fill(1,0,'title'):
            self.rewind(-2)
            self.fill(0,1,'title')
            self.fill(0,1,'number')
        #
        self.skip(0,1)
        self.fill(1,0,'vote_type')
        self.skip(1,0)
        self.fill(1,0,'date_sec')
        # uprawnieni, za, obecni, przeciw, nieobecni, wstrzymujacy, nieodddane, kworum
        self.skip(0,1)
        self.fill(1,0,'entitle', parser=int)
        self.skip(1,0)
        self.fill(1,0,'votes_in_favor', parser=int)

        self.skip(0,1)
        self.fill(1,0,'present', parser=int)
        self.skip(1,0)
        self.fill(1,0,'votes_against', parser=int)

        self.skip(0,1)
        self.fill(1,0,'absent', parser=int)
        self.skip(1,0)
        self.fill(1,0,'votes_abstain', parser=int)

        #self.skip(0,1)  # two empty cells don't have object..
        #self.skip(1,0)
        self.skip(0,1)
        self.fill(1,0,'votes_no_vote', parser=int)

        self.maybe_skip(0,1, cond=lambda t: t.lower().find('kworum')>=0)
        self.skip(0,1) # urpawnienie do glosowania
        self.skip(0,1) # LP
        self.skip(5,0) # the rest of ...
        while True:
            council_vote = {}
            self.fill(0,1, 'ordinal_number', obj=council_vote, parser=int)
            self.fill(1,0, 'name', obj=council_vote)
            self.fill(1,0, 'vote', obj=council_vote)
            self._data['votes'].append(council_vote)

            council_vote = {}
            fields_set=0
            fields_set += self.maybe_fill(1,0, 'ordinal_number', obj=council_vote, parser=int)
            fields_set += self.maybe_fill(1,0, 'name', obj=council_vote)
            fields_set += self.maybe_fill(1,0, 'vote', obj=council_vote)
            if fields_set==3:
                self._data['votes'].append(council_vote)
            else:
                self.rewind(-3)
                break

# <codecell>

def extract_from_file(in_path, out_path):
    # extract data from .pdf
    file_handler = open(in_path, encoding='cp1250') # tried also: iso8859_2
    t_objs = create_state_machine2(file_handler)
    if DEBUG:
        s = sorted(t_objs, key=lambda x: float(x._x))
        s = sorted(s, key=lambda x: float(x._y), reverse=True)
        for t in s:
            print(t)
    # line_counter = 0
    # for line in file_handler:
    #     line_counter+=1
    #     if line.find('/CreationDate') >= 0:
    #         print(line_counter, line)
    #     elif line.find('%% Contents for page ') >= 0:  # page start
    #         print(line_counter, line)
    #     elif line.find('endstream') >= 0:
    #         print(line_counter, 'stream end')
    #     elif line.find('endobj') >= 0:
    #         print(line_counter, 'obj end')
    #     elif line.find('obj\n') >= 0:
    #         print(line_counter, 'obj start')
    #     elif line.find('stream\n') >= 0:
    #         print(line_counter, 'stream begin')

    file_handler.close()
    parser = Parser(t_objs)
    parser.parse()
    #print(parser)
    #print(json.dumps(parser._data, indent=2, sort_keys=True))
    json.dump(parser._data, open(out_path, 'w'), indent=2, sort_keys=True)
    print('succeeded')

in_file='/home/orian/tmp/olsztyn_analiza_pdf/data/decoded/g6.pdf'
out_file = in_file.replace('.pdf', '.json')
extract_from_file(in_file, out_file)

# <codecell>


# <codecell>


