import pandas as pd
import plotly.offline as offline
import matplotlib.pyplot as plt
from matplotlib.finance import *
import matplotlib.dates as mdates
from plotly.tools import FigureFactory as FF
# from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
# offline.init_notebook_mode()
import glob
import argparse
import os
import decimal
from shutil import copyfile, move

import imgkit

import subprocess

def drange(x, y, jump):
    while x < y:
        yield float(x)
        x += decimal.Decimal(jump)


def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input',
                        help='a csv file of stock data', required=True)
    parser.add_argument('-l', '--seq_len',
                        help='num of sequence length', default=20)
    parser.add_argument('-lf', '--label_file',
                        help='a label_file')
    parser.add_argument('-d', '--dimension',
                        help='a dimension value')
    parser.add_argument('-t', '--dataset_type',
                        help='training or testing datasets')
    parser.add_argument('-m', '--mode',
                        help='mode of preprocessing data', required=True)
    args = parser.parse_args()
    if args.mode == 'ohlc2cs':
        ohlc2cs(args.input, args.seq_len, args.dataset_type)
    if args.mode == 'createLabel':
        createLabel(args.input, args.seq_len)
    if args.mode == 'img2dt':
        image2dataset(args.input, args.label_file)

def image2dataset(input, label_file):

    label_dict = {}
    with open(label_file) as f:
        for line in f:
            (key, val) = line.split(',')
            label_dict[key] = val.rstrip()
    # print(label_dict)
    # print(list(label_dict.values())[list(label_dict.keys()).index('FTSE-80')])
    path = "{}/{}".format(os.getcwd(), input)
    # df = pd.DataFrame()
    # os.chdir("{}/{}/".format(os.getcwd(),input))
    # print(os.getcwd())

    for filename in os.listdir(input):
        print(filename)
        if filename is not '':
            label = list(label_dict.values())[
                list(label_dict.keys()).index("{}".format(filename[:-4]))]
            # name = list(label_dict.keys())[list(label_dict.values()).index("{}".format(label))]
            #print("name : {}".format(name))
            # print(filename)
            new_name = "{}{}.png".format(label, filename[:-4])
            print("rename {} to {}".format(filename, new_name))
            os.rename("{}/{}".format(path,filename), "{}/{}".format(path,new_name))

    folders = ['1','0']
    for folder in folders:
        if not os.path.exists("{}/classes/{}".format(path,folder)):
            os.makedirs("{}/classes/{}".format(path,folder))

    for filename in os.listdir(input):
        if filename is not '':
            # print(filename[:1])
            if filename[:1] == "1":
                move("{}/{}".format(path,filename), "{}/classes/1/{}".format(path,filename))
            elif filename[:1] == "0":
                move("{}/{}".format(path,filename), "{}/classes/0/{}".format(path,filename))

def createLabel(fname, seq_len):
    print("Creating label . . .")

    df = pd.read_csv(fname, parse_dates=True, index_col=0)
    df.fillna(0)

    df.reset_index(inplace=True)
    df['Date'] = df['Date'].map(mdates.date2num)
    for i in range(0, len(df)):
        c = df.ix[i:i+int(seq_len)-1,:]
        starting = 0
        endvalue = 0
        label = ""
        if len(c) == int(seq_len):
            for idx, val in enumerate(c['Adj Close']):
                if idx == 0:
                    starting = float(val)
                if idx == len(c) - 1:
                    endvalue = float(val)
            if endvalue > starting:
                label = 1
            else:
                label = 0
            with open("{}_label_{}.txt".format(fname[11:-4],seq_len), 'a') as the_file:
                the_file.write("{}-{},{}".format(fname[11:-4], i, label))
                the_file.write("\n")


def ohlc2cs(fname, seq_len, dataset_type):
    print("Converting olhc to candlestick")
    path = "{}".format(os.getcwd())
    print(path)
    if not os.path.exists("{}/dataset/{}/{}".format(path,seq_len,dataset_type)):
        os.makedirs("{}/dataset/{}/{}".format(path,seq_len,dataset_type))

    df = pd.read_csv(fname, parse_dates=True, index_col=0)
    df.fillna(0)

    df.reset_index(inplace=True)
    df['Date'] = df['Date'].map(mdates.date2num)
    for i in range(0, len(df)):
        c = df.ix[i:i+int(seq_len)-1,:]
        if len(c) == int(seq_len):
            fig = plt.figure(figsize=(2.5974025974,3.1746031746))

            ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1, axisbg = 'black')
            candlestick_ohlc(ax1, c.values, colorup='g', colordown='r')
            ax1.set_xticklabels([])
            ax1.set_yticklabels([])
            ax1.tick_params(axis=u'both', which=u'both',length=0)
            pngfile='dataset/{}/{}/{}-{}.png'.format(seq_len,dataset_type,fname[11:-4], i)
            print("{}".format(pngfile))
            fig.savefig(pngfile,bbox_inches='tight', pad_inches=0)
            plt.close(fig)

if __name__ == '__main__':
    main()
