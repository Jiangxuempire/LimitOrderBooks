
from Enums.TimeSeriesTypes import TimeSeriesTypes
from Enums.TimeSeriesSource import TimeSeriesSource
from Analytics.LimitOrderBookSeries import LimitOrderBookSeries
import numpy as np
import pandas as pd


class TimeSeriesFactory:

    def __init__(self, limit_order_books):
        self.books = limit_order_books
        #self.num_books = len(self.books)
        self.err_msg = 'series type not recognised'

    def create_time_series(self, time_series_types, start_time=34200, time_interval=5):
        """
        :param time_series_types: time series type
        :param start_time: start time
        :param time_interval: time interval
        :return: time series as list
        """
        if time_series_types == TimeSeriesTypes.price:
            bid_output = list()
            ask_output = list()
            index = list()
            book_num = 1
            for book in self.books:
                #if book[0][-1].submission_time > start_time:
                if book.time >= start_time:
                    bid_output.append(book.bid_queue)
                    ask_output.append(book.ask_queue)
                    index.append(start_time)
                    start_time += time_interval
                book_num += 1
            return pd.Series(bid_output, index=index), pd.Series(ask_output, index=index)
        elif time_series_types == TimeSeriesTypes.size:
            bid_output = list()
            ask_output = list()
            for book in self.books:
                if book.time > start_time:
                    bid_output.append(book[0][-1].size)
                    ask_output.append(book[1][0].size)
                    start_time += time_interval
            return bid_output, ask_output
        elif time_series_types == TimeSeriesTypes.full_size:
            bid_output = list()
            ask_output = list()
            for book in self.books:
                if book[0][-1].submission_time > start_time:
                    bid_orders = [book[0][i].size for i in range(0, len(book[0]))]
                    ask_orders = [book[1][i].size for i in range(0, len(book[1]))]
                    bid_output.append(np.sum(bid_orders))
                    ask_output.append(np.sum(ask_orders))
                    start_time += time_interval
            return bid_output, ask_output
        elif time_series_types == TimeSeriesTypes.mid_price:
            bid_price, ask_price = self.create_time_series(TimeSeriesTypes.price,start_time, time_interval)
            bid_price=bid_price.tolist()
            ask_price = ask_price.tolist()
            mid_price = list()
            for i in range(0, len(bid_price)):
                mid_price.append(0.5 * (bid_price[i] + ask_price[i]))
            return mid_price
        elif time_series_types == TimeSeriesTypes.imbalance:
            imbalance_output = list()
            index = list()
            for book in self.books:
                if book[0][-1].submission_time > start_time:
                    imbalance_output.append(book[1][0].price - book[0][-1].price)
                    index.append(start_time)
                    start_time += time_interval
            return pd.Series(imbalance_output, index=index)
        else:
            raise NotImplementedError(self.err_msg)

    def create_time_series_order_book(self,order_book_data,
                                      time_series_types,
                                      start_time=34200,
                                      time_interval=5):

        if time_series_types == TimeSeriesTypes.price:
            bid_values = order_book_data['BidPrice1']
            ask_values = order_book_data['AskPrice1']
            bid_output = list()
            ask_output = list()
            index = list()
            for time in bid_values.index:
                # if book[0][-1].submission_time > start_time:
                if time >= start_time:
                    if isinstance(bid_values[time], pd.Series):
                        out = bid_values[time]
                        bid_output.append(out.iloc[0])
                    else:
                        bid_output.append(bid_values[time])
                    if isinstance(ask_values[time], pd.Series):
                        out = ask_values[time]
                        ask_output.append(out.iloc[1])
                    else:
                        ask_output.append(ask_values[time])
                    index.append(start_time)
                    start_time += time_interval
            bid_series = LimitOrderBookSeries(bid_output, index)
            ask_series = LimitOrderBookSeries(ask_output, index)
            return bid_series, ask_series
        elif time_series_types == TimeSeriesTypes.size:
            bid_size = order_book_data['BidSize1']
            ask_size = order_book_data['AskSize1']
            bid_output = list()
            ask_output = list()
            index = list()
            for time in bid_size.index:
                if time >= start_time:
                    if isinstance(bid_size[time], pd.Series):
                        out = bid_size[time]
                        bid_output.append(out.iloc[0])
                    else:
                        bid_output.append(bid_size[time])
                    if isinstance(ask_size[time], pd.Series):
                        out = ask_size[time]
                        ask_output.append(out.iloc[1])
                    else:
                        ask_output.append(ask_size[time])
                    index.append(start_time)
                    start_time += time_interval
            bid_series = LimitOrderBookSeries(bid_output, index)
            ask_series = LimitOrderBookSeries(ask_output, index)
            return bid_series, ask_series
        elif time_series_types == TimeSeriesTypes.full_size:
            bid_sizes = ['BidSize1', 'BidSize2', 'BidSize3', 'BidSize4', 'BidSize5']
            ask_sizes = ['AskSize1', 'AskSize2', 'AskSize3', 'AskSize4', 'AskSize5']
            bid = list()
            ask = list()
            for idx in order_book_data.index:
                bid_size = 0.0
                ask_size = 0.0
                for size in bid_sizes:
                    bid_size += order_book_data[size][idx]
                for size in ask_sizes:
                    ask_size += order_book_data[size][idx]
                bid.append(bid_size)
                ask.append(ask_size)
            bid_output = LimitOrderBookSeries(bid, order_book_data.index)
            ask_output = LimitOrderBookSeries(ask, order_book_data.index)
            return bid_output, ask_output
        elif time_series_types == TimeSeriesTypes.mid_price:
            bid, ask = self.create_time_series_order_book(order_book_data,
                                                          TimeSeriesTypes.price,
                                                          start_time,
                                                          time_interval)
            bid_price = bid.tolist()
            ask_price = ask.tolist()
            mid_price = list()
            for i in range(0, len(bid_price)):
                mid_price.append(0.5 * (bid_price[i] + ask_price[i]))

            output = LimitOrderBookSeries(mid_price, bid.index)
            return output
        elif time_series_types == TimeSeriesTypes.imbalance:
            bid, ask = self.create_time_series_order_book(order_book_data,
                                                          TimeSeriesTypes.price,
                                                          start_time,
                                                          time_interval)
            bid_price = bid.tolist()
            ask_price = ask.tolist()
            imbalance_output = [ask_price[i] - bid_price[i] for i in range(0, len(bid_price))]
            output = LimitOrderBookSeries(imbalance_output, bid.index)
            return output
        else:
            raise NotImplementedError(self.err_msg)

