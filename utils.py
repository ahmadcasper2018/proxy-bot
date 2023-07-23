from collections import defaultdict


def filter_by_state(proxy_list, state):
    filtered_proxies = [proxy for proxy in proxy_list if proxy["Region"] == state]
    return filtered_proxies


def filter_by_country(proxy_list, country):
    filtered_proxies = [proxy for proxy in proxy_list if proxy["Country"] == country]
    return filtered_proxies


def filter_proxy_by_isp(proxy_list, target_isp):
    filtered_proxy_list = [proxy for proxy in proxy_list if proxy["ISP"] == target_isp]
    return filtered_proxy_list


def bind_country_state(proxy_list):
    country_region_dict = defaultdict(list)
    for proxy in proxy_list:
        country_region_dict[proxy["Country"]].extend(
            region
            for region in [proxy["Region"]]
            if region not in country_region_dict[proxy["Country"]]
        )
    return dict(country_region_dict)


def sort_proxies_by_speed(proxies_list):
    sorted_proxies = sorted(proxies_list, key=lambda x: x["Speed"])
    return sorted_proxies


def sort_proxies_by_quality(proxies_list):
    sorted_proxies = sorted(proxies_list, key=lambda x: x["UpTimeQuality"])
    return sorted_proxies


def get_states(proxy_list, country):
    return bind_country_state(proxy_list).get(country)


def bind_country_isp(proxy_list):
    country_isp_dict = defaultdict(set)
    for proxy in proxy_list:
        country_isp_dict[proxy["Country"]].add(proxy["ISP"])
    return {country: list(isps) for country, isps in country_isp_dict.items()}
