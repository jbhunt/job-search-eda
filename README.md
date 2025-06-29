# job-search-eda
This is a repository for exploratory data analysis (EDA) of my post-PhD job search. As of June 27, 2025, I have considered and collected data for 79 job opportunities, and for 48 of these 79 opportunities (61%), I submitted completed applications. 58.3% of my applications received no response, 37.5% resulted in an explicit rejection, and 4.17% resulted in at least one interview. I received job offers from 2 employers, one for a postdoctoral fellowship, and one for a postiion as a biostatistician.

# Salary
Between November 11, 2024 and June 27, 2025, I applied to 45 jobs that listed at least a minimum target salary. This visualization shows the salary ranges grouped by industry and sorted by the mean within-industry minimum salary. The shaded boxes indicate the within-industry mean minimum and mean maximum salary. Unsurprisingly, jobs in academia - mostly postdoctoral fellowships - were associated with some of the lowest salaries; whereas jobs in Tech had some of the highest salaries. The vertical gray line on the left indicates my annual stipend as a graduated student the last year in my program ($38,110).
<p align="center">
  <img src="docs/imgs/salary_ranges.png" width="500" alt="Animated demo">
</p>

# Outcome
For the 48 job applications I submitted, I recorded whether I was able to convert these applications into invitations to interview. I was interested in understanding what factors influenced my "success" in converting my applications to interviews, so I used logistic regression to estimate the effect of these factors:
- Referral: Did I have a personal connection that referred me for the job, yes (1) or no (0)
- Industry: Was the job in a non-academic (0) or academic setting (1)
- Pay minimum: Minmum listed salary (Normalized 0-1)
- Pay maximum: Maximum listed salary (Normalize 0-1)
Here are the odds ratios and 95% confidence intervals for each of the factors. Odds ratios of less than 1 indicate lower odds of converting applicaitons to interviews and odds ratios greater than 1 indicate higher odds of converting applications to interviews. 
<p align="center">
  <img src="docs/imgs/regression_coefficients.png" width="700" alt="Animated demo">
</p>
The factor with the greatest odds ratio was "Referral;" I was more likely to get an invitation to interview if I had a personal connection to the job. I was also more likely to get an interview for jobs in academic settings. And finally, it seems like I was less likely to get interviews the greater the minimum and maximum salary.