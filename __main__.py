from flask import Flask
from opencensus.ext.prometheus import stats_exporter as prometheus
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_key as tag_key_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.tags import tag_value as tag_value_module


############# 1. Opencensus Configuration #############

# 1.1 Create measurement for visitors (used in process_data)
m_visitor_counts = measure_module.MeasureInt("visitor_counts", "The number of visitors")


# 1.2 Create stats_recorder to record measure
stats_recorder = stats_module.stats.stats_recorder


# 1.3 Predefine the tag keys (status, error)
key_status = tag_key_module.TagKey("status")
key_error = tag_key_module.TagKey("error")


# 1.4 View for visitor -> Just count!
visitor_count_view = view_module.View("visitors_count", "The number of blog visitors : using CountAggregation()",
                                   [key_status, key_error],
                                   m_visitor_counts,
                                   aggregation_module.CountAggregation())

# 1.4 View for visitor -> Sum aggregation of Visitors
visitor_sum_view = view_module.View("visitors_sum", "The number of blog visitors : using SumAggregation()",
                                   [key_status, key_error],
                                   m_visitor_counts,
                                   aggregation_module.SumAggregation())


# 1.5 Register view and exporter to view_manager
def setup_opencensus_prom_exporter():
    exporter = prometheus.new_stats_exporter(prometheus.Options(namespace="alicek106", port=8088))

    view_manager = stats_module.stats.view_manager
    view_manager.register_exporter(exporter)
    view_manager.register_view(visitor_count_view)
    view_manager.register_view(visitor_sum_view)


# Create measurement and record values (Called from Flask)
def process_data():

    # Let's start measurement :D
    # Create the measure_map into which we'll insert the measurements
    mmap = stats_recorder.new_measurement_map()

    # Record new sum -> Increment value only 1 (new request : new visitor!)
    mmap.measure_int_put(m_visitor_counts, 1)

    tmap = tag_map_module.TagMap()
    tmap.insert(key_error, tag_value_module.TagValue("None"))
    tmap.insert(key_status, tag_value_module.TagValue("200"))

    # Insert the tag map finally
    mmap.record(tmap)


############# 2. Flask Configuration ##############

app = Flask(__name__)

@app.route('/')
def path_root():
    process_data()
    greeting = 'Thank you for visiting alicek106 blog!'
    return greeting

if __name__ == "__main__":
    setup_opencensus_prom_exporter()
    app.run(host='0.0.0.0', port=8080)