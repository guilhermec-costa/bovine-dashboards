def manage_downloads(status_list):
    download_status = []
    for status_tuple in status_list:
        empty_dict = {}
        empty_dict[status_tuple[0]] = status_tuple[1]
        download_status.append((empty_dict, status_tuple[2]))
    return download_status