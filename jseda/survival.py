import polars as pl
import numpy as np
from datetime import datetime
from lifelines import KaplanMeierFitter
from matplotlib import pyplot as plt

class SurvivalAnalysis():
    """
    """

    def __init__(self, data):
        """
        """

        self.df = pl.read_csv(data).filter(
            pl.col('application_status').is_in([
                'Rejected',
                'No response to application',
            ]) & \
            pl.col('date_submitted').is_null().not_()
        )

        return
    
    def plot(
        self,
        maximum_lifetime=120
        ):
        """
        """

        outcome = self.df['outcome'].to_numpy()
        E = np.full(outcome.size, 0)
        E[outcome < 1] = 1
        T = self.df['days_to_outcome'].to_numpy()
        for i, t1 in enumerate(self.df['date_submitted']):
            if E[i] == 1:
                continue
            t1 = datetime.strptime(t1, "%m/%d/%Y")
            t2 = datetime.today()
            dt = (t2 - t1).days
            if maximum_lifetime is not None and dt > maximum_lifetime:
                E[i] = 1
                T[i] = maximum_lifetime
            else:
                T[i] = dt

        #
        m = np.isnan(T)
        E = np.delete(E, m)
        T = np.delete(T, m)

        #
        km = KaplanMeierFitter()
        km.fit(T, E)
        x = km.timeline
        y = km.survival_function_.to_numpy().ravel()
        ci = km.confidence_interval_.to_numpy()

        #
        # y = 1 - y
        # ci = 1 - ci

        #
        fig, ax = plt.subplots()
        ax.step(x, y, where='post', color='C0')
        ax.fill_between(x, ci[:, 0], ci[:, 1], step='post', color='C0', alpha=0.2, edgecolor='none')
        ax.set_xlabel('Time from submitting application (days)')
        ax.set_ylabel('Probability of application "survival"')
        fig.tight_layout()

        return E, T