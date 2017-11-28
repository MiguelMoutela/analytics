from .aou_analytics import *


class AouSummary:
    
    
    def __init__(self, file_path, start_date, end_date, interval):

        rows = get_rows(file_path)
        counts_by_site_per_day = get_counts_by_site_per_day(rows, start_date, end_date)

        counts_by_site_per_interval = get_counts_by_site_per_interval(counts_by_site_per_day, interval)

        milestones = get_milestones(counts_by_site_per_interval)

        dates = sorted(counts_by_site_per_interval['PITT'].keys())
        sites_at_milestone = get_sites_at_milestone(milestones, dates)

        counts_per_interval = get_counts_per_interval(counts_by_site_per_interval)

        cumulative_totals_by_site = get_cumulative_totals_by_site(counts_by_site_per_interval, dates)

        cumulative_totals = get_cumulative_totals(cumulative_totals_by_site, dates)

        # Cross-site average full participant enrollment per interval.
        # A mean adjustment excludes sites that haven't enrolled anyone yet.
        means_per_interval = get_means_per_interval(counts_per_interval, sites_at_milestone)

        milestones = get_milestones(counts_by_site_per_interval)

        dates = sorted(counts_by_site_per_interval['PITT'].keys())
        sites_at_milestone = get_sites_at_milestone(milestones, dates)

        counts_per_interval = get_counts_per_interval(counts_by_site_per_interval)

        cumulative_totals_by_site = get_cumulative_totals_by_site(counts_by_site_per_interval, dates)

        cumulative_totals = get_cumulative_totals(cumulative_totals_by_site, dates)

        # Cross-site average full participant enrollment per interval.
        # A mean adjustment excludes sites that haven't enrolled anyone yet.
        means_per_interval = get_means_per_interval(counts_per_interval, sites_at_milestone)


        csv_interval_totals = get_csv_interval_totals(
            counts_by_site_per_interval, '', interval, counts_per_interval,
            means_per_interval, cumulative_totals_by_site, cumulative_totals
        )

        self.counts_by_site_per_interval = counts_by_site_per_interval
        self.counts_per_interval = counts_per_interval
        self.means_per_interval = means_per_interval
        self.cumulative_totals_by_site = cumulative_totals_by_site
        self.cumulative_totals = cumulative_totals
        self.csv_interval_totals = csv_interval_totals
