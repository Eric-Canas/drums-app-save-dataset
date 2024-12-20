from keras.callbacks import Callback
import os
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve
import numpy as np

class PlotingCallback(Callback):
    """
    Generate and save the plots for the given validation data each period epochs. As Callback
    """
    def __init__(self, path, period=1):
        super().__init__()
        self.path = path
        self.period = period

    def on_epoch_end(self, epoch, logs={}):
        if epoch % self.period == 0 and epoch != 0:
            [os.remove(os.path.join(self.path, file)) for file in os.listdir(self.path) if file.endswith('.png')]
            used_metrics = [metric for metric in logs.keys() if 'val' not in metric]
            if type(list(logs.values())[0]) is not list:
                history = self.model.history.history
            else:
                history = logs
            for label in used_metrics:
                self.plot(history=history, path=self.path, label=label)

    def plot(self, history, path, label, xlabel='Epochs'):
        over_train, over_val = history[label], history['val_' + label]

        plt.plot(over_train)
        plt.plot(over_val)
        plt.title('Model ' + label.title())
        plt.ylabel(label.title())
        plt.xlabel(xlabel)
        plt.legend(['Training', 'Validation'], loc='upper left')

        if not os.path.exists(path=path):
            os.mkdir(path=path)

        name = label.title() + '.png'

        plt.savefig(os.path.join(path, name))
        plt.close()

class ConfusionMatrix(Callback):
    """
    Generate and save the plots for the given validation data each period epochs. As Callback
    """

    def __init__(self, path, train_set, val_set, period=1):
        super().__init__()
        self.path = path
        self.period = period
        self.train_set = train_set
        self.val_set = val_set

    def on_epoch_end(self, epoch, logs={}):
        if epoch % self.period == 0 and epoch != 0:
            self.plot(path=self.path)

    def plot(self,  path, th=0.5):
        for set, set_name in ((self.train_set, 'Train'), (self.val_set, 'Val')):
            y_true, y_pred, y_prob_pred = [], [], []
            for x, y in set:
                y_true.append(y)
                y_pred.append(self.model.predict(x) > th)
            y_true, y_pred = np.concatenate(y_true).astype(np.int), np.concatenate(y_pred).astype(np.int)
            conf_mat = confusion_matrix(y_true=y_true, y_pred=y_pred, normalize='true')
            plt.matshow(conf_mat, vmin=0.0, vmax=1.0)
            plt.title('{set} - No Hit Acc: {n}% - Hit Acc: {m}%'.format(set=set_name, n=round(conf_mat[0,0]*100,2),
                                                                        m=round(conf_mat[1,1]*100,2)))
            plt.ylabel('Ground Truth')
            plt.xlabel('Prediction')
            plt.colorbar()

            if not os.path.exists(path=path):
                os.mkdir(path=path)

            name = '{set} Confusion Matrix.png'.format(set=set_name)

            plt.savefig(os.path.join(path, name))
            plt.close()

class RocAndPRCurvesCallback(Callback):
    """
    Generate and save the plots for the given validation data each period epochs. As Callback
    """

    def __init__(self, path, train_set, val_set, period=1):
        super().__init__()
        self.path = path
        self.period = period
        self.train_set = train_set
        self.val_set = val_set

    def on_epoch_end(self, epoch, logs={}):
        if epoch % self.period == 0 and epoch != 0:
            self.plot(path=self.path)

    def plot(self, path):
        for set, set_name in ((self.train_set, 'Train'), (self.val_set, 'Val')):
            y_true, y_pred = [], []
            for x, y in set:
                y_true.append(y)
                y_pred.append(self.model.predict(x))
            y_true, y_pred = np.concatenate(y_true), np.concatenate(y_pred).astype(np.float)
            for curve, curve_name, xlabel, ylabel, first_axis in zip((roc_curve, precision_recall_curve), ('Roc Curve', 'Precision-Recall Curve'),
                                                            ('False Positive Rate', 'Recall'), ('True Positive Rate', 'Precision'),
                                                            (0, 1)):
                crv = curve(y_true, y_pred)
                x, y = crv[first_axis], crv[1-first_axis]
                plt.plot(x, y)
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.title('{set} {curve}'.format(set=set_name, curve=curve_name))
                if first_axis==0:
                    area = auc(x=x, y=y)
                    plt.legend(['Area Under the Curve : {:.3f})'.format(area)], loc='best')

                if not os.path.exists(path=path):
                    os.mkdir(path=path)

                name = '{curve} {set}.png'.format(curve=curve_name, set=set_name)

                plt.savefig(os.path.join(path, name))
                plt.close()

