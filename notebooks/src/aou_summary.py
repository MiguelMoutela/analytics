from .utils import *


class AouSummary:
    
    
    def __init__(self, file_path, start_date, end_date, interval):

        rows = self.get_rows(file_path)
        counts_by_site_per_day = self.get_counts_by_site_per_day(rows, start_date, end_date)

        counts_by_site_per_interval = self.get_counts_by_site_per_interval(counts_by_site_per_day, interval)

        milestones = self.get_milestones(counts_by_site_per_interval)

        dates = sorted(counts_by_site_per_interval['PITT'].keys())
        sites_at_milestone = self.get_sites_at_milestone(milestones, dates)

        counts_per_interval = self.get_counts_per_interval(counts_by_site_per_interval)

        cumulative_totals_by_site = self.get_cumulative_totals_by_site(counts_by_site_per_interval, dates)

        cumulative_totals = self.get_cumulative_totals(cumulative_totals_by_site, dates)

        # Cross-site average full participant enrollment per interval.
        # A mean adjustment excludes sites that haven't enrolled anyone yet.
        means_per_interval = self.get_means_per_interval(counts_per_interval, sites_at_milestone)

        milestones = self.get_milestones(counts_by_site_per_interval)

        dates = sorted(counts_by_site_per_interval['PITT'].keys())
        sites_at_milestone = self.get_sites_at_milestone(milestones, dates)

        counts_per_interval = self.get_counts_per_interval(counts_by_site_per_interval)

        cumulative_totals_by_site = self.get_cumulative_totals_by_site(counts_by_site_per_interval, dates)

        cumulative_totals = self.get_cumulative_totals(cumulative_totals_by_site, dates)

        # Cross-site average full participant enrollment per interval.
        # A mean adjustment excludes sites that haven't enrolled anyone yet.
        means_per_interval = self.get_means_per_interval(counts_per_interval, sites_at_milestone)

        csv_interval_totals = self.get_csv_interval_totals(
            counts_by_site_per_interval, '', interval, counts_per_interval,
            means_per_interval, cumulative_totals_by_site, cumulative_totals
        )

        self.counts_by_site_per_interval = counts_by_site_per_interval
        self.counts_per_interval = counts_per_interval
        self.means_per_interval = means_per_interval
        self.cumulative_totals_by_site = cumulative_totals_by_site
        self.cumulative_totals = cumulative_totals
        self.csv_interval_totals = csv_interval_totals
        
    @staticmethod
    def get_rows(file_path):
        """Returns raw data from participants_view SQL output, as a list of lists
        """
        '''
        SQL query used to generate values in 'lists':

        SELECT  
            hpo,
            enrollment_status,
            CAST(sign_up_time AS date) sign_up_time,
            CAST(consent_for_study_enrollment_time AS date) consent_for_study_enrollment_time,
            CAST(consent_for_electronic_health_records_time AS date) consent_for_electronic_health_records_time,
            CAST(physical_measurements_time AS date) physical_measurements_time,
            CAST(questionnaire_on_the_basics_time AS date) questionnaire_on_the_basics_time,
            CAST(questionnaire_on_overall_health_time AS date) questionnaire_on_overall_health_time,
            CAST(questionnaire_on_lifestyle_time AS date) questionnaire_on_lifestyle_time,
            CAST(sample_status_1sst8_time AS date) sample_status_1sst8_time,
            CAST(sample_status_1pst8_time AS date) sample_status_1pst8_time,
            CAST(sample_status_1hep4_time AS date) sample_status_1hep4_time,
            CAST(sample_status_1ed04_time AS date) sample_status_1ed04_time,
            CAST(sample_status_1ed10_time AS date) sample_status_1ed10_time,
            CAST(sample_status_2ed10_time AS date) sample_status_2ed10_time,
            CAST(sample_status_1ur10_time AS date) sample_status_1ur10_time,
            CAST(sample_status_1sal_time AS date) sample_status_1sal_time,
            CAST(suspension_time AS date) suspension_time,
            CAST(withdrawal_time AS date) withdrawal_time
        FROM rdr.participant_view 
        WHERE 
            hpo <> 'TEST' 
        ORDER BY sign_up_time;
        '''
        lists = sql_to_lists(file_path)
        headers = lists[0]
        rows = lists[1:]
        return rows

    @staticmethod
    def truncate_counts(counts_by_site_per_day, start_date, end_date):
        # Dates in *dates.txt seem to be past-shifted by one day
        # relative to those in Dashboard and HealthPro.
        # The latter set seems to be correct -- e.g. weekends are 0-filled -- 
        # so we account for that with some shifting here. 
        # See also later uses of "dates[:-1]", dates[1:], etc.
        shifted_end_date = previous_date(end_date)

        # Limit counts to only those in the requested date range
        all_dates = date_range(start_date, shifted_end_date)
        truncated_counts = {}

        for hpo in counts_by_site_per_day:
            truncated_counts[hpo] = {}
            for date in all_dates:
                if date not in counts_by_site_per_day[hpo]:
                    # Fill in missing dates with '0'
                    truncated_counts[hpo][date] = 0
                else:
                    truncated_counts[hpo][date] = counts_by_site_per_day[hpo][date]

        return truncated_counts

    @staticmethod
    def get_counts_by_site_per_day(rows, start_date, end_date):
        """Count of participants who reached "full participant" status on a given day.

        For example (not real data):
          {
             'PITT': {
                '2017-10-01': 50,
                '2017-10-02': 53,
                ...
             },
             ...
          }
        """
        counts_by_site_per_day = {}

        for row_columns in rows:
            # Each item in "rows" represents a participant -- particularly,
            # the set of dates when that participant completed a specified event
            # in the enrollment lifecycle
            hpo = row_columns[0]

            '''
            # Dead code, but perhaps useful documentation

            consent_for_study_enrollment_time = row_columns[2]
            consent_for_electronic_health_records_time = row_columns[3]
            physical_measurements_time = row_columns[4]

            # These correspond to "num_completed_baseline_ppi_modules"
            questionnaire_on_the_basics = row_columns[5]
            questionnaire_on_overall_health_time = row_columns[6]
            questionnaire_on_lifestyle_time = row_columns[7]

            # We assume these three samples comprise "samples_to_isolate_dna"
            sample_status_1ed04_time = row_columns[11] # EDTA DNA 4 mL
            sample_status_1ed10_time = row_columns[12] # 1st EDTA DNA 10 mL
            sample_status_2ed10_time = row_columns[13] # 2nd EDTA DNA 10 mL
            '''

            # Gather all the dates of each lifecycle phase that needs to be
            # passed in order to become a full participant
            dates = row_columns[2:8] + row_columns[11:14]

            # Get the latest -- the most recent -- of those dates
            most_recent_date = sorted(dates)[-1]

            # Increment by 1 the number of full participants enrolled
            # in this HPO (i.e. high-level recruitment origin, "site")
            # on this date
            if hpo in counts_by_site_per_day:
                counted_days = counts_by_site_per_day[hpo]
                if most_recent_date in counted_days:
                    counts_by_site_per_day[hpo][most_recent_date] += 1
                else:
                    counts_by_site_per_day[hpo][most_recent_date] = 1
            else:
                counts_by_site_per_day[hpo] = {most_recent_date: 1}

        counts_by_site_per_day = AouSummary.truncate_counts(counts_by_site_per_day, start_date, end_date)
        return counts_by_site_per_day

    @staticmethod
    def get_counts_by_site_per_interval(counts_by_site_per_day, interval):
        """Roll up days into weekly or monthly bins, if requested
        """
        if interval == 'day':
            return counts_by_site_per_day

        counts_by_site_per_interval = {}
        for hpo in counts_by_site_per_day:
            counts_by_site_per_interval[hpo] = {}
            dates = list(counts_by_site_per_day[hpo].keys())
            if interval == 'week':
                dates = list(reversed(dates))
                # Here, weeks are considered simply seven-day periods
                # beginning with the requested 'end_date'.  
                # This interval aligns with Dashboard, 
                # but would probably be better labeled '7-day'.
                # 
                # TODO: Enable counting at the most recent Sunday. 
                # This would align with the calendrical week.
                days_by_weeks = n_sized_chunks(dates, 7)
                for days_by_week in days_by_weeks:
                    week_date = days_by_week[0]
                    week_total = 0
                    for date in days_by_week:
                        week_total += counts_by_site_per_day[hpo][date]
                    counts_by_site_per_interval[hpo][week_date] = week_total
            elif interval == 'month':
                # Note: these are calendrical months.
                # TODO: Add '30-day' interval, to align with Dashboard.
                # TODO: Reconcile 'month' counts with month-long 'day' range, and Dashboard.
                counts_by_month = {}
                for date in dates:
                    day_count = counts_by_site_per_day[hpo][date]
                    year, bare_month, day = date.split('-')
                    month = year + '-' + bare_month # e.g. 2017-10
                    if month not in counts_by_month:
                        counts_by_month[month] = day_count
                    else:
                        counts_by_month[month] += day_count
                counts_by_site_per_interval[hpo] = counts_by_month

        return counts_by_site_per_interval
    
    @staticmethod
    def get_milestones(counts_by_site_per_interval):    
        """Returns milestones by site, e.g. date of first full participant enrollment
        """
        milestones = {}
        for hpo in counts_by_site_per_interval:
            milestones[hpo] = {}

        for hpo in counts_by_site_per_interval:
            dates = sorted(counts_by_site_per_interval[hpo].keys())
            for date in dates:
                count = counts_by_site_per_interval[hpo][date]
                if count > 0 and 'first_fp' not in milestones[hpo]:
                    milestones[hpo]['first_fp'] = date
            if 'first_fp' not in milestones[hpo]:
                milestones[hpo]['first_fp'] = '0'
        return milestones

    @staticmethod
    def get_sites_at_milestone(milestones, dates):
        """Return dictionary reporting the number of sites that have achieved a given
        milestone by a particular date.  

        For example, if eight sites had enrolled at least one full participant (FP) 
        as of October 1st, 2017, then we would see:

          print(count_of_sites_at_milestone['first_fp']['2017-10-01'])
          8

        Such counts are used when calculating cross-site statistics over time.
        """

        # Initialize variable with zero-filled values by date 
        sites_at_milestone = {'first_fp': {}}
        for date in dates:
            sites_at_milestone['first_fp'][date] = 0

        for hpo in milestones:
            first_fp_date = int(milestones[hpo]['first_fp'].replace('-', ''))
            for date in dates:
                first_fp_count = 0
                date_int = int(date.replace('-', ''))
                if first_fp_date > 0 and first_fp_date <= date_int:
                    first_fp_count += 1
                    sites_at_milestone['first_fp'][date] += 1

        return sites_at_milestone

    @staticmethod
    def get_counts_per_interval(counts_by_site_per_interval):
        counts_per_interval = {}
        for hpo in counts_by_site_per_interval:
            for date in counts_by_site_per_interval[hpo]:
                count = counts_by_site_per_interval[hpo][date]
                prev_count = 0
                if date not in counts_per_interval:
                    counts_per_interval[date] = count
                else:
                    counts_per_interval[date] += count
        return counts_per_interval

    @staticmethod
    def get_cumulative_totals_by_site(counts_by_site_per_interval, dates):
        """Gets the running total by site
        """
        cumulative_totals_by_site = {}
        for hpo in counts_by_site_per_interval:
            cumulative_totals_by_site[hpo] = {}
            for i, date in enumerate(dates):
                count = counts_by_site_per_interval[hpo][date]
                if i == 0:
                    cumulative_totals_by_site[hpo][date] = count
                else:
                    prev_date = dates[i - 1]
                    prev_count = cumulative_totals_by_site[hpo][prev_date]
                    cumulative_totals_by_site[hpo][date] = count + prev_count
        return cumulative_totals_by_site

    @staticmethod
    def get_cumulative_totals(cumulative_totals_by_site, dates):
        """Collapse cumulative totals by date by site into cumulative totals by date
        """
        cumulative_totals = {}
        for date in dates:
            cumulative_totals[date] = 0
        for hpo in cumulative_totals_by_site:
            for date in dates:
                cumulative_totals[date] += cumulative_totals_by_site[hpo][date]
        return cumulative_totals

    @staticmethod
    def get_means_per_interval(counts_per_interval, sites_at_milestone):
        """Returns cross-site average full participant enrollment per interval.
        This adjusted mean excludes sites that haven't enrolled anyone yet.
        """
        means_per_interval = {}
        for date in counts_per_interval:
            count = counts_per_interval[date]
            sites_at_first_fp = sites_at_milestone['first_fp'][date]
            if sites_at_first_fp == 0:
                mean = 0
            else:
                mean = round(count/sites_at_first_fp)
            means_per_interval[date] = mean
        return means_per_interval

    @staticmethod
    def get_csv_interval_totals(
        counts_by_site_per_interval, hpo_of_interest, interval, counts_per_interval, 
        means_per_interval, cumulative_totals_by_site, cumulative_totals
    ):
        # Print a CSV table with first row listing dates, 
        # and each subsequent row listing counts per date by site
        output = []
        totals = {}
        for hpo in counts_by_site_per_interval:
            dates = sorted(counts_by_site_per_interval[hpo].keys())
            if hpo == 'PITT':
                # Get header row.  See note re past-shifting above.
                output.append('Recruitment origin,' + ','.join(dates[:-1]))
            # Get counts in same order as sorted dates.  See note re past-shifting above.
            counts = [counts_by_site_per_interval[hpo][date] for date in dates[1:]]
            totals[hpo] = 0
            for date in dates:
                totals[hpo] += counts_by_site_per_interval[hpo][date]
            counts.insert(0, hpo) 
            row = ','.join([str(value) for value in counts])
            if hpo_of_interest != '' and hpo != hpo_of_interest:
                # If we're analyzing only one HPO and this isn't it, skip it
                continue
            output.append(row)

        # Add a row to the CSV table generated above, giving total per interval on each date
        dates = sorted(counts_per_interval.keys())
        total_counts = [counts_per_interval[date] for date in dates[1:]]
        total_counts.insert(0, 'Total throughput per ' + interval)
        row = ','.join([str(value) for value in total_counts])
        output.append(row)

        # Add row to CSV table to report site mean on each date
        dates = sorted(means_per_interval.keys())
        means = [means_per_interval[date] for date in dates[1:]]
        means.insert(0, 'Mean site throughput (adjusted)')
        row = ','.join([str(value) for value in means])
        output.append(row)

        # Add row to CSV table to report cumulative total
        dates = sorted(cumulative_totals.keys())
        counts = [cumulative_totals[date] for date in dates[1:]]
        counts.insert(0, 'Cumulative total')
        row = ','.join([str(value) for value in counts])
        output.append(row)

        # Add row to CSV table, giving the number of intervals since start.  E.g week 1, 2...
        interval_index = [str(i) for i in range(0, len(dates) - 1)]
        interval_index.insert(0, interval + ' index')
        row = ','.join([str(value) for value in interval_index])
        output.append(row)

        return output