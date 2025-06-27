from matplotlib import pylab as plt
import polars as pl
import numpy as np

class SalaryRangeFigure():
    """
    """

    def __init__(self, data):
        """
        """

        self.df = pl.read_csv(data)
        self.df = self.df.with_columns(
            pl.col('Industry').fill_null('Other')
        )
        self.df = self.df.filter(
            ~(pl.col("Pay minimum").is_null() & pl.col("Pay maximum").is_null())
        )

        return
    
    def plot(self):
        """
        """

        fig, ax = plt.subplots()

        salary_ranges = {}
        for industry in self.df['Industry'].unique():
            subset = self.df.filter(self.df['Industry'] == industry)
            subset = subset.with_columns(
                pl.col("Pay minimum")
                .str.replace_all(r"[\$,]", "")   # drop $ and commas
                .cast(pl.Int64)                  # turn the digits into integers
            )
            subset = subset.with_columns(
                pl.col("Pay maximum")
                .str.replace_all(r"[\$,]", "")   # drop $ and commas
                .cast(pl.Int64)                  # turn the digits into integers
            )
            salary_ranges[industry] = np.vstack([
                subset['Pay minimum'].to_numpy(),
                subset['Pay maximum'].to_numpy()
            ]).T

        #
        cmap = plt.get_cmap('tab10')
        mean_pay_minimum = {}
        for industry in salary_ranges.keys():
            mean_pay_minimum[industry] = np.nanmean(salary_ranges[industry][:, 0]).item()
        index = np.argsort(list(mean_pay_minimum.values()))
        y = 0
        for i in index:
            industry = list(mean_pay_minimum.keys())[i]
            salary_data = salary_ranges[industry]
            index_ = np.argsort(salary_data[:, 0])
            x1 = salary_data[index_, 0]
            x2 = salary_data[index_, 1]

            # Lines
            ax.hlines(
                np.arange(y, y + len(x1), 1),
                x1,
                x2,
                color=cmap(i),
                label=industry
            )

            # Patches
            ax.fill_between(
                [np.nanmean(x1), np.nanmean(x2)],
                y - 0.5, y + len(x1) - 0.5,
                color=cmap(i),
                alpha=0.15,
                edgecolor='none',
            )
            
            # Markers
            for ii in np.argsort(salary_data[:, 0]):
                x1, x2 = salary_data[ii, :]
                ax.scatter([x1, x2], [y, y], color=cmap(i), s=5)
                y += 1

        ax.set_xlim([0, ax.get_xlim()[1]])
        ax.set_xticklabels(ax.get_xticks() / 1000)
        ax.set_xlabel('Salary (K)')
        ax.set_ylabel('Opportunity #')
        ax.legend(
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            borderaxespad=0.6,
        )
        fig.set_figwidth(5)
        fig.set_figheight(7)
        fig.tight_layout()

        return fig, ax