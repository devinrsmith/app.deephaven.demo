from deephaven import KafkaTools as kt
from deephaven import ComboAggregateFactory as caf
from deephaven.TableTools import merge, newTable, stringCol, doubleCol

def get_kafka_settings():
    kafka_host = 'demo-kafka.c.deephaven-oss.internal'
    return {
        'bootstrap.servers' : '{}:9092'.format(kafka_host), 
        'schema.registry.url' : 'http://{}:8081'.format(kafka_host)
    }

def get_trades_stream():
    return kt.consumeToTable(
        get_kafka_settings(),
        'io.deephaven.crypto.kafka.TradesTopic',
        key = kt.IGNORE,
        value = kt.avro('io.deephaven.crypto.kafka.TradesTopic-io.deephaven.crypto.Trade'),
        offsets=kt.ALL_PARTITIONS_SEEK_TO_BEGINNING,
        table_type='stream')

def get_quotes_stream():
    return kt.consumeToTable(
        get_kafka_settings(),
        'io.deephaven.crypto.kafka.QuotesTopic',
        key = kt.IGNORE,
        value = kt.avro('io.deephaven.crypto.kafka.QuotesTopic-io.deephaven.crypto.Quote'),
        table_type='stream')

def get_quotes_latest(quotes):
    return quotes.lastBy("Exchange", "Instrument")

def get_trades_latest(trades):
    return trades.lastBy("Exchange", "Instrument")

def get_trades_summary(trades, usd_prices):
    return trades\
        .updateView("BaseVolume=Price*Size")\
        .by(caf.AggCombo(
            caf.AggCount("Count"),
            caf.AggSum("Volume=Size","BaseVolume"),
            caf.AggAvg("AvgPrice=Price")),
            "Exchange",
            "Instrument",
            "Type")\
        .updateView("Currency=Instrument.split(`/`)[1]")\
        .naturalJoin(usd_prices, "Currency")\
        .updateView("DollarVolume=USD * BaseVolume")

def get_usd_prices(quotes_latest):
    usd_table = newTable(stringCol("Currency", "USD", "USDT"), doubleCol("USD", 1.0, 1.0))
    quotes_median = quotes_latest.where(
        "!isNull(Timestamp)",
        "!isNull(Bid)",
        "!isNull(Ask)",
        "Instrument.endsWith(`/USD`) || Instrument.endsWith(`/USDT`)")\
        .view("Currency=Instrument.split(`/`)[0]", "USD=(Bid+Ask)/2")\
        .medianBy("Currency")
    return merge(usd_table, quotes_median)

#quotes_stream = get_quotes_stream()
#quotes_latest = get_quotes_latest(quotes_stream)
#usd_prices = get_usd_prices(quotes_latest)

#trades_stream = get_trades_stream()
#trades_latest = get_trades_latest(trades_stream)
#trades_summary = get_trades_summary(trades_stream, usd_prices)
