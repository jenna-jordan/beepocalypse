import pandas as pd
import requests
import time


def query_solr(query: str, fields: list):
    """ 
    This function sends a query to the Solr API and returns a dataframe with the results.
    """
    # the url to send the query to
    baseurl = # censored for security reasons

    # incorporate parameters
    q = "q=" + query
    fl = "fl=" + ",".join(fields)

    # define initial url for query
    rows = 0
    init_query = baseurl + fl + "&" + q + "&rows=" + str(rows)

    # figure out how many results to get
    time.sleep(5)
    init_query_results = requests.get(init_query)

    # exception handling in case something goes wrong with the query
    if init_query_results.status_code == 200:
        records_found = init_query_results.json()['response']['numFound']
    else:
        records = []

    # now get the actual data
    rows = records_found
    final_query = baseurl + fl + "&" + q + "&rows=" + str(rows)

    time.sleep(5)
    final_query_results = requests.get(final_query)

    # exception handling in case something goes wrong with the query
    if final_query_results.status_code == 200:
        records = final_query_results.json()['response']['docs']
    else:
        records = []

    if len(records) > 0:
        print("Success! Your query returned " + str(records_found) + " documents.")
    else:
        print("Something went wrong.")

    df = pd.DataFrame(records)
    return df


def filter_results(df, filter_type, lower_limit):
    """
    This function will filter a query to exclude likely irrelevant results. 
    There are two types of filters: Solr's relevancy score or term frequency counts.
    """
    if filter_type == 'score':
        mask = df['score'] >= lower_limit
        final_df = df[mask]
        final_df = final_df.drop(columns=['score'])
    elif filter_type == 'termfreq':
        termfreq_cols = [col for col in df if col.startswith('termfreq')]
        df['termfreq_sum'] = df[termfreq_cols].sum(axis=1)
        mask = df['termfreq_sum'] >= lower_limit
        final_df = df[mask]
        final_df = final_df.drop(columns=termfreq_cols)
        final_df = final_df.drop(columns=['termfreq_sum'])
    else:
        final_df = df

    return final_df


def to_daily_timeseries(df, query_name: str, base_ts, publisher=True):
    """
    This function will transform the raw results into a time-series that counts how many articles match the query per day.
    """
    if publisher:
        grouping_columns = ['publication_date', 'publisher']
    else:
        grouping_columns = ['publication_date']

    df['publication_date'] = pd.to_datetime(df['publication_date'].astype('str').str[:10], format='%Y-%m-%d')
    df_gb = df.groupby(grouping_columns).agg({'aid': 'nunique'}).reset_index().rename(columns={'aid': query_name})
    final_df = base_ts.merge(df_gb, on=grouping_columns, how='left').fillna(0).sort_values(grouping_columns).set_index(
        grouping_columns)
    return final_df


def run_all_queries(queries: list, fields: list, base_ts, publisher=True, prune=False):
    """
    This function enables multiple queries to be run and then transformed into the time-series format.
    """
    if publisher:
        grouping_columns = ['publication_date', 'publisher']
    else:
        grouping_columns = ['publication_date']

    base_df = base_ts.sort_values(grouping_columns).set_index(grouping_columns)

    # loop through the queries, merging each into the base and then updating the base
    for q in queries:
        if prune:
            all_fields = fields.copy()
            all_fields.extend(q['add_fields'])
            result = query_solr(q['query'], all_fields)
            filtered_results = filter_results(result, filter_type=q['filter_method'][0], lower_limit=q['filter_method'][1])
            new_table = to_daily_timeseries(filtered_results, q['name'], base_ts, publisher=publisher)
        else:
            result = query_solr(q['query'], fields)
            new_table = to_daily_timeseries(result, q['name'], base_ts, publisher=publisher)
        
        base_df = base_df.merge(new_table, left_index=True, right_index=True, how='left')

    return base_df