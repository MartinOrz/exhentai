# coding=utf-8
__author__ = 'v_mading'

import time
import requests
import threading
import queue


class Dispatcher(threading.Thread):
    """
    监视线程，也负责工作的维护
    """

    def __init__(self, date, worker_number):
        threading.Thread.__init__(self)
        self.name = 'Dispatcher'
        self.queue = queue.Queue()
        self.date = date
        self.url = 'http://adtag-internal.baidu.com/ctp/creativity/getStoredCreativities.do?&startTime=' + date + \
                   '000000' + '&endTime=' + date + '235959&size=1000&page='
        for i in range(500):
            self.queue.put(i + 1)
        self.done = False
        self.workers = []
        self.dic = {}

        for i in range(worker_number):
            self.workers.append(Worker('Worker' + str(i), self.date, self.url, self.queue, self.dic))

    def run(self):

        for worker in self.workers:
            worker.start()

        while not self.done:

            awake = 0
            for worker in self.workers:
                # 查询线程工作状态
                if not worker.done:
                    awake += 1

            if awake == 0:
                # 当任务队列结束，并且所有线程都结束时，任务结束
                self.done = True
                for worker in self.workers:
                    worker.stop()
            time.sleep(2)

        done = 0
        errs = ''
        for p in self.dic:
            now = self.dic[p]
            if now > 0:
                done += now
            else:
                errs += str(p) + ','
        with open(r'd:\ctp_done', 'a', encoding='utf-8') as file:
            file.write(self.date + ' has done: ' + str(done) + ', err pages: ' + errs + '\n')


class Worker(threading.Thread):
    """
    下载工作类，即一个线程
    """

    def __init__(self, name, date, url, que, dic):
        threading.Thread.__init__(self)
        self.name = name
        self.date = date
        self.url = url
        self.done = False  # 任务是否已完成
        self.queue = que  # 任务队列
        self.dic = dic

    def wake_up(self):
        """
        唤醒此线程，重新开始进行下载任务
        """
        self.done = False
        self.start()

    def stop(self):
        """
        彻底终止此线程
        """
        print(self.name + ' done.')
        self.done = True

    def run(self):
        """
        执行下载任务
        """
        while not self.done:
            try:
                page = self.queue.get(timeout=5)  # 阻塞模式，最多等待5秒
                url = self.url + str(page)
                r = requests.get(url)
                result = r.content.decode('utf-8')
                try:
                    done = int(result)
                except:
                    done = -1
                if done == 0:
                    self.stop()
                else:
                    self.dic[page] = done
                print('[' + self.name + ']' + self.date + ', page: ' + str(page) + ', ' + str(done))
            except queue.Empty:  # empty即取出任务失败，没有任务可用时
                self.stop()

def read(inf, mod, outf1, outf2):
    d = {}
    rem = []
    with open(inf, encoding='utf-8') as file:
        for line in file:
            if line[-1] == '\n':
                line = line[:-1]
            parms = line.split('\t')
            adid = int(parms[0])
            if adid % 7 == mod:
                version = int(parms[3])
                if adid not in d:
                    d[adid] = (version, line)
                elif version > d[adid][0]:
                    d[adid] = (version, line)
                    rem.append(adid)
    rem = set(rem)
    with open(outf1, 'a', encoding='utf-8') as file:
        for adid in d:
            file.write(d[adid][1] + '\n')
    with open(outf2, 'a', encoding='utf-8') as file:
        for adid in rem:
            file.write(d[adid][1] + '\n')


if __name__ == '__main__':
    outf1 = r'd:\ctp\beidou_recover_new'
    outf2 = r'd:\ctp\beidou_recover_inc'
    with open(r'd:\ctp\do', encoding='utf-8') as file:
        lines = file.readlines()
    lines = [line[:-1] if line[-1] == '\n' else line for line in lines]
    for i in (0, 1, 2, 3, 4, 5, 6):
        for line in lines:
            read(line, i, outf1, outf2)
            print(line + ' ' + str(i))

