import os
import time
from pathlib import Path

import copy
import numpy as np
import torch
from torch import nn

from ...tqdm import BTqdm
from ...log import BLogger
from ...drawer.terminal import BColor, BAppearance
from .earlystop import reloadByLoss
from .earlystop import stopByLoss, stopByAcc
from .earlystop import stopByLossDelta, stopByAccDelta
from .earlystop import stopByOverfitting

def inputs_function(inputs):
    return inputs
def outputs_function(outputs):
    return outputs
def labels_function(labels):
    return labels

class _saveDuringTrain:
    def __init__(self, path, rounds):
        self.path = path
        self.rounds = rounds
        self.cnt = 0
    def __call__(self):
        self.cnt += 1
        if self.cnt > self.rounds:
            self.cnt = 0
            return True
        return False

class BTrainer:
    def __init__(self, model, train_loader, val_loader, optimizer, criterion, device,
                 lrScheduler=None,
                 isBinaryCls=False, isParallel=False, isSpikingjelly=False):
        '''
        训练:\n
        train_eval_s\n
        训练前函数:\n
        load_model, load_optimizer, load_lrScheduler, set_logger, set_stop_by_acc\n
        训练后函数:\n
        save_latest_checkpoint, save_best_checkpoint, calculate_model
        :param model:
        :param train_loader:
        :param val_loader:
        :param optimizer:
        :param criterion:
        :param device:
        :param lrScheduler:
        :param isBinaryCls: 若是二分类, 则输出额外信息
        :param isParallel: 是否多GPU
        :param isSpikingjelly: 是否为SNN
        '''
        self.train_acc_lst = []
        self.train_loss_lst = []
        self.val_acc_lst = []
        self.val_f1_lst = []
        self.val_L0_True_lst = []
        self.val_L1_True_lst = []

        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.lrScheduler = lrScheduler
        self.isBinaryCls = isBinaryCls
        self.isParallel = isParallel
        self.isSpikingjelly = isSpikingjelly

        self.model.to(self.device)

        self.__isTraining = False
        # save_temp
        self.__save_during_train = None
        # logger
        self.__log = None
        # early stop
        self.__stop_by_acc = None
        self.__stop_by_acc_delta = None
        self.__stop_by_loss = None
        self.__stop_by_loss_delta = None
        self.__stop_by_overfitting = None
        # early reload
        self.__reload_by_loss = None
        # save_best
        self.__best_acc = 0
        self.__best_model_state_dict = None
        self.__best_optimizer_state_dict = None
        self.__best_lrScheduler_state_dict = None

        if self.isParallel:
            if str(self.device) == str(torch.device("cuda")):
                if torch.cuda.device_count() > 1:
                    print(f"当前GPU数量:{torch.cuda.device_count()}, 使用多GPU训练")
                    self.model = nn.DataParallel(self.model)
                else:
                    print(f"当前GPU数量:{torch.cuda.device_count()}, 使用单GPU训练")

    def train_eval_s(self,
                     epochs,
                     inputs_func=inputs_function,
                     outputs_func=outputs_function,
                     labels_func=labels_function):
        '''
        :param epochs:
        :param inputs_func: 对inputs的处理函数
        :param outputs_func: 对outputs的处理函数
        :param labels_func: 对labels的处理函数
        :return:
        '''
        self.__isTraining = True

        # 检查inputs_func是否为函数
        if not callable(inputs_func):
            raise ValueError("inputs_func传入的参数应该要是一个函数!!!")
        # 检查outputs_func是否为函数
        if not callable(outputs_func):
            raise ValueError("outputs_func传入的参数应该要是一个函数!!!")
        # 检查labels_func是否为函数
        if not callable(labels_func):
            raise ValueError("labels_func传入的参数应该要是一个函数!!!")

        for epoch in range(epochs):
            train_acc, train_loss, current_lr = self.__train_once(epoch, epochs, inputs_func, outputs_func, labels_func)
            val_acc = self.__eval_once(inputs_func, outputs_func, labels_func)
            # 日志
            if self.__log is not None:
                self.__log.toFile(
                    f'Epoch [{epoch}/{epochs}], lr: {current_lr:.2e} | '
                    f'train_loss: {train_loss:.3f} | train_acc: {train_acc:.3f}, val_acc: {val_acc:.3f}'
                )
            # 保存模型
            if self.__save_during_train is not None:
                if self.__save_during_train():
                    self.save_best_checkpoint(self.__save_during_train.path)
            # 早停
            if self.__stop_by_acc is not None:
                if self.__stop_by_acc(train_loss):
                    info = f'模型在连续{self.__stop_by_acc.rounds}个epoch内停滞, 触发stop_by_acc'
                    print(info)
                    if self.__log is not None:
                        self.__log.toFile(info)
                    break
            # 早停
            if self.__stop_by_acc_delta is not None:
                if self.__stop_by_acc_delta(val_acc):
                    info = f'模型在连续{self.__stop_by_acc_delta.rounds}个epoch内过拟合, 触发stop_by_acc_delta'
                    print(info)
                    if self.__log is not None:
                        self.__log.toFile(info)
                    break
            # 早停
            if self.__stop_by_loss is not None:
                if self.__stop_by_loss(train_loss):
                    info = f'模型在连续{self.__stop_by_loss.rounds}个epoch内停滞, 触发stop_by_loss'
                    print(info)
                    if self.__log is not None:
                        self.__log.toFile(info)
                    break
            # 早停
            if self.__stop_by_loss_delta is not None:
                if self.__stop_by_loss_delta(train_loss):
                    info = f'模型在连续{self.__stop_by_loss_delta.rounds}个epoch内停滞, 触发stop_by_loss_delta'
                    print(info)
                    if self.__log is not None:
                        self.__log.toFile(info)
                    break
            # 过拟合
            if self.__stop_by_overfitting is not None:
                if self.__stop_by_overfitting(train_acc, val_acc):
                    info = f'模型在连续{self.__stop_by_overfitting.rounds}个epoch内过拟合, 触发stop_by_overfitting'
                    print(info)
                    if self.__log is not None:
                        self.__log.toFile(info)
                    break
            # 重加载
            if self.__reload_by_loss is not None:
                match self.__reload_by_loss(train_loss):
                    case 'continue':
                        pass
                    case 'reload':
                        info = f'模型触发reload_by_loss(第{self.__reload_by_loss.cnt_reload}次加载)'
                        print(info)
                        if self.__log is not None:
                            self.__log.toFile(info)
                        # 加载
                        self.model.load_state_dict(self.__best_model_state_dict)
                        self.optimizer.load_state_dict(self.__best_optimizer_state_dict)
                        if self.lrScheduler is not None:
                            self.lrScheduler.load_state_dict(self.__best_lrScheduler_state_dict)
                        self.calculate_model()
                    case 'stop':
                        info = f'模型在{self.__reload_by_loss.max_reload_count}次reload_by_loss后停滞, 停止训练'
                        print(info)
                        if self.__log is not None:
                            self.__log.toFile(info)
                        break
    def calculate_model(self, dataloader=None, model=None):
        '''
        如果不指定, 则用类内的
        :param dataloader: 默认self.val_loader
        :param model: 默认self.model
        :return:
        '''
        if dataloader==None:
            dataloader = self.val_loader
        if model==None:
            model = self.model
        model.eval()
        correct = 0
        total = 0
        y_true = []
        y_pred = []
        inference_time = []
        with torch.no_grad():
            for inputs, labels in dataloader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                start_time = time.time()
                outputs = model(inputs)
                end_time = time.time()
                _, predicted = torch.max(outputs, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                y_true.extend(labels.cpu().numpy())
                y_pred.extend(predicted.cpu().numpy())
                inference_time.append(end_time - start_time)
                if self.isSpikingjelly:
                    from spikingjelly.activation_based import functional
                    functional.reset_net(model)
            # 平均推理时间
            inference_time = sum(inference_time) / len(inference_time)
            # 精确度
            accuracy = correct / total
            # 参数量
            params = sum(p.numel() for p in model.parameters())
            info = f'[calculate] accuracy: {accuracy:.3f}, inference_time: {inference_time:.2e}s, params: {params/1e3}K'
            print(info)
            if self.__log is not None:
                self.__log.toFile(info)
            if self.isBinaryCls:
                from sklearn.metrics import confusion_matrix
                mat = confusion_matrix(y_true, y_pred)
                print('mat:\n', mat)

                TN, FP, FN, TP = mat.ravel()

                f1 = self.__get_f1(TP, FP, FN)
                print('f1:', f1)

                L0_True = self.__get_L0_True(TN, FP)
                print('L0_True:', L0_True)

                L1_True = self.__get_L1_True(FN, TP)
                print('L1_True:', L1_True)

    def save_latest_checkpoint(self, path):
        '''
        字典checkpoint包含net, optimizer, lrScheduler
        '''
        parent_path = Path(path).parent
        os.makedirs(parent_path, exist_ok=True)

        checkpoint = {
            'model': self.model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'lrScheduler': self.lrScheduler.state_dict()
        }
        torch.save(checkpoint, path)
        print(f"latest_checkpoint已保存到{path}")

    def save_best_checkpoint(self, path):
        '''
        字典checkpoint包含net, optimizer, lrScheduler
        '''
        parent_path = Path(path).parent
        os.makedirs(parent_path, exist_ok=True)

        checkpoint = {
            'model': self.__best_model_state_dict,
            'optimizer': self.__best_optimizer_state_dict,
            'lrScheduler': self.__best_lrScheduler_state_dict
        }
        torch.save(checkpoint, path)
        print(f"best_checkpoint已保存到{path}")
    def load_model(self, path):
        checkpoint = torch.load(path, map_location='cpu')
        self.model.load_state_dict(checkpoint['model'])
        self.model.to(self.device)
        print(f"model 已从{path}加载")
    def load_optimizer(self, path):
        checkpoint = torch.load(path)
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        print(f"optimizer 已从{path}加载")
    def load_lrScheduler(self, path):
        checkpoint = torch.load(path)
        if self.lrScheduler is not None and checkpoint['lrScheduler'] is not None:
            self.lrScheduler.load_state_dict(checkpoint['lrScheduler'])
            print(f"lrScheduler 已从{path}加载")
        else:
            print(f"lrScheduler为None")

    def set_logger(self, logPath, mode='a'):
        '''
        请在训练前设置set_logger
        :param logPath:
        :param mode: 'a', 'w'
        :return:
        '''
        self.__log = BLogger(logPath, ifTime=True)
        if mode == 'a':
            pass
        if mode == 'w':
            self.__log.clearFile()

        self.__log.toFile("model="+str(self.model), ifTime=False)
        if self.lrScheduler is not None:
            self.__log.toFile("lrScheduler="+str(self.lrScheduler.__class__.__name__), ifTime=False)
        print(f'日志将保存到{logPath}')
    def set_save_during_train(self, path, rounds=10):
        '''
        请在训练前设置set_save_during_train
        '''
        self.__save_during_train = _saveDuringTrain(path, rounds)
    def set_stop_by_acc(self, rounds=10, delta=0.01):
        '''
        请在训练前设置set_stop_by_acc
        :param rounds: 连续rounds次, val_acc - max_val_acc > delta, 则停止训练
        :return:
        '''
        self.__stop_by_acc = stopByAcc(rounds=rounds, delta=delta)
    def set_stop_by_overfitting(self, rounds=10, delta=0.1):
        '''
        请在训练前设置set_stop_by_overfitting
        :param rounds: 连续rounds次, train_acc - val_acc > delta, 则停止训练
        :return:
        '''
        self.__stop_by_overfitting = stopByOverfitting(rounds=rounds, delta=delta)
    def set_stop_by_acc_delta(self, rounds=10, delta=0.003):
        '''
        请在训练前设置set_stop_by_acc_delta
        :param rounds: 连续rounds次, |before_acc - val_acc| <= delta, 则停止训练
        :return:
        '''
        self.__stop_by_acc_delta = stopByAccDelta(rounds=rounds, delta=delta)
    def set_stop_by_loss(self, rounds=10, delta=0.01):
        '''
        请在训练前设置set_stop_by_loss
        :param rounds: 连续rounds次, train_loss - min_train_loss > delta, 则停止训练
        :return:
        '''
        self.__stop_by_loss = stopByLoss(rounds=rounds, delta=delta)
    def set_stop_by_loss_delta(self, rounds=10, delta=0.002):
        '''
        请在训练前设置set_stop_by_loss_delta
        :param rounds: 连续rounds次, |before_loss - now_loss| <= delta, 则停止训练
        :return:
        '''
        self.__stop_by_loss_delta = stopByLossDelta(rounds=rounds, delta=delta)
    def set_reload_by_loss(self, max_reload_count=5, reload_rounds=10, delta=0.01, max_minLoss=5):
        '''
        请在训练前设置set_reload_by_loss
        :param rounds: 连续rounds次都是train_loss > min_train_loss + delta
        :return:
        '''
        self.__reload_by_loss = reloadByLoss(max_reload_count, reload_rounds, delta, max_minLoss)

    def draw(self, jpgPath, isShow=False):
        parent_path = Path(jpgPath).parent
        os.makedirs(parent_path, exist_ok=True)

        import matplotlib
        if isShow==False:
            matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        palette = sns.color_palette("Set2", 3)

        plt.figure(figsize=(8, 8))
        plt.subplots_adjust(hspace=0.4)

        plt.subplot(3, 1, 1)
        # 每十个画一次(防止点多卡顿)
        temp = [x for i, x in enumerate(self.train_loss_lst) if (i + 1) % 10 == 0]
        plt.plot(temp, color="red", label="train_loss")
        plt.xlabel("iter 1/10")
        plt.ylabel("loss")
        plt.legend(loc='upper right')

        plt.subplot(3, 1, 2)
        plt.plot(self.train_acc_lst, color="red", label="train_acc")
        plt.plot(self.val_acc_lst, color="blue", label="val_acc")
        plt.xlabel("epoch")
        plt.ylabel("acc")
        plt.ylim(-0.05, 1.05)
        plt.legend(loc='lower right')

        if self.isBinaryCls:
            plt.subplot(3, 1, 3)
            plt.plot(self.val_f1_lst, color=palette[0], label="f1")
            plt.plot(self.val_L0_True_lst, color=palette[1], label="L0_True")
            plt.plot(self.val_L1_True_lst, color=palette[2], label="L1_True")
            plt.xlabel("epoch")
            plt.ylabel("score")
            plt.ylim(-0.05, 1.05)
            plt.legend(loc='lower right')

        plt.savefig(jpgPath)
        print(f"picture已保存到{jpgPath}")
        if isShow:
            plt.show()
        plt.close()

    # def __pretrainChecking(self):
    #     lst = [self.__stop_by_acc, self.__stop_by_loss, self.__reload_by_loss]
    #     cnt = 0
    #     for x in lst:
    #         if x is not None:
    #             cnt += 1
    #     assert cnt <= 1, f"{BColor.YELLOW}earlyStop和earlyReload总共只能设置一个!!!{BColor.RESET}"

    def __train_once(self, epoch, epochs, inputs_func, outputs_func, labels_func):
        bar = BTqdm(total=len(self.train_loader))
        current_lr = self.optimizer.param_groups[0]['lr']

        self.model.train()
        correct = 0
        total = 0
        losses = 0
        for iter, (inputs, labels) in enumerate(self.train_loader):
            # 基本训练
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            labels = labels_func(labels)
            inputs = inputs_func(inputs)
            outputs = self.model(inputs)
            outputs = outputs_func(outputs)

            loss = self.criterion(outputs, labels)
            self.optimizer.zero_grad()  # 清零梯度
            loss.backward()  # 计算梯度
            self.optimizer.step()  # 更新参数
            # SNN
            if self.isSpikingjelly:
                from spikingjelly.activation_based import functional
                functional.reset_net(self.model)
            # 进度条
            bar.update(1,
                       setting=BColor.BLUE+BAppearance.HIGHLIGHT,
                       prefix=f"{BColor.BLUE}Epoch [{epoch}/{epochs}]",
                       suffix=f"lr: {current_lr:.2e}, loss: {loss.item():.3f}")
            # 数据记录
            self.train_loss_lst.append(loss.item())
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            losses += loss.item()
        accuracy = correct / total
        train_loss = losses / len(self.train_loader)
        print(f'Epoch [{epoch}/{epochs}], train_loss: {train_loss:.3f}, train_Acc: {accuracy:.3f}', end='')
        self.train_acc_lst.append(accuracy)
        # 更新学习率
        if self.lrScheduler:
            self.lrScheduler.step()

        return accuracy, train_loss, current_lr

    def __eval_once(self, inputs_func, outputs_func, labels_func):
        self.model.eval()
        correct = 0
        total = 0
        y_true = []
        y_pred = []
        with torch.no_grad():
            for inputs, labels in self.val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                labels = labels_func(labels)
                inputs = inputs_func(inputs)
                outputs = self.model(inputs)
                outputs = outputs_func(outputs)
                _, predicted = torch.max(outputs, 1)

                if self.isSpikingjelly:
                    from spikingjelly.activation_based import functional
                    functional.reset_net(self.model)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            # 记录accuracy
            accuracy = correct / total
            print(f', val_Acc: {accuracy:.3f}')
            self.val_acc_lst.append(accuracy)

            # 保存最优模型
            if accuracy > self.__best_acc:
                self.__best_acc = accuracy
                self.__best_model_state_dict = copy.deepcopy(self.model.state_dict())
                self.__best_optimizer_state_dict = copy.deepcopy(self.optimizer.state_dict())
                self.__best_lrScheduler_state_dict = copy.deepcopy(self.lrScheduler.state_dict()) if self.lrScheduler else None

            if self.isBinaryCls:
                from sklearn.metrics import confusion_matrix
                TN, FP, FN, TP = confusion_matrix(y_true, y_pred).ravel()

                f1 = self.__get_f1(TP, FP, FN)
                self.val_f1_lst.append(f1)

                L0_True = self.__get_L0_True(TN, FP)
                self.val_L0_True_lst.append(L0_True)

                L1_True = self.__get_L1_True(FN, TP)
                self.val_L1_True_lst.append(L1_True)

        return accuracy

    def __get_precision(self, TP, FP):
        if TP + FP == 0:
            return np.nan
        return TP / (self, TP + FP)

    def __get_recall(self, TP, FN):
        return TP / (TP + FN)

    def __get_f1(self, TP, FP, FN):
        precision = self.__get_precision(TP, FP)
        recall = self.__get_recall(TP, FN)
        if np.isnan(precision):
            return np.nan
        f1 = 2 * precision * recall / (precision + recall)
        return f1

    def __get_L0_True(self, TN, FP):
        return TN / (TN + FP)

    def __get_L1_True(self, FN, TP):
        return TP / (TP + FN)