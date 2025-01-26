class stopByAcc:
    def __init__(self, rounds, delta=0.01):
        self.rounds = rounds
        self.delta = delta
        self.max_val_acc = 0
        self.cnt = 0
    def __call__(self, val_acc):
        if val_acc <= self.max_val_acc - self.delta:
            self.cnt += 1
        if val_acc > self.max_val_acc:
            self.max_val_acc = val_acc
            self.cnt = 0
        if self.cnt > self.rounds:
            return True
        return False

class stopByAccDelta:
    def __init__(self, rounds, delta=0.1):
        '''
        连续rounds次, train_acc - val_acc > delta, 则停止训练
        '''
        self.rounds = rounds
        self.delta = delta
        self.cnt = 0
    def __call__(self, train_acc, val_acc):
        if train_acc - val_acc > self.delta:
            self.cnt += 1
        else:
            self.cnt = 0
        if self.cnt > self.rounds:
            return True
        return False

class stopByLoss:
    def __init__(self, rounds, delta=0.01):
        '''
        连续rounds次, train_loss - min_train_loss > delta, 则停止训练
        '''
        self.rounds = rounds
        self.delta = delta
        self.min_trainLoss = float('inf')
        self.cnt = 0
    def __call__(self, train_loss):
        if train_loss >= self.min_trainLoss + self.delta:
            self.cnt += 1
        if train_loss < self.min_trainLoss:
            self.min_trainLoss = train_loss
            self.cnt = 0
        if self.cnt > self.rounds:
            return True
        return False

class stopByLossDelta:
    def __init__(self, rounds, delta=0.01):
        '''
        连续rounds次, |before_loss - now_loss| <= delta, 则停止训练
        '''
        self.rounds = rounds
        self.delta = delta
        self.before_loss = float('inf')
        self.cnt = 0
    def __call__(self, train_loss):
        if -self.delta <= (train_loss - self.before_loss) <= self.delta:
            self.cnt += 1
            self.before_loss = train_loss
        elif self.cnt > 0:
            self.cnt -= 1
            self.before_loss = train_loss
        else:
            self.before_loss = train_loss

        if self.cnt > self.rounds:
            return True
        return False
class reloadByLoss:
    def __init__(self, max_reload_count, reload_rounds, delta=0.01, max_minLoss=5):
        '''
        基于stopByLoss\n
        max_reload_count: 最大重新加载次数\n
        reload_rounds: 多少轮内loss不减，则重新加载best_model
        delta: 浮动范围
        max_minLoss: 多少轮内loss都小于delta, 代表训练完毕, 则停止训练
        '''
        self.reload_rounds = reload_rounds
        self.delta = delta
        self.min_valLoss = float('inf')
        self.cnt_trigger = 0

        self.max_reload_count = max_reload_count
        self.cnt_reload = 0

        self.max_minLoss = max_minLoss
        self.cnt_minLoss = 0
    def __call__(self, val_loss):
        if val_loss >= self.min_valLoss + self.delta:
            self.cnt_trigger += 1
        if val_loss < self.min_valLoss:
            self.min_valLoss = val_loss
            self.cnt_trigger = 0
        if self.cnt_trigger > self.reload_rounds:
            self.cnt_reload += 1
            self.cnt_trigger = 0
            if self.cnt_reload > self.max_reload_count:
                return 'stop'
            return 'reload'
        if val_loss < self.delta:
            self.cnt_minLoss += 1
        if self.cnt_minLoss > self.max_minLoss:
            return 'stop'
        return 'continue'

