#!/usr/bin/env python
# coding: utf-8

# # Temperatures

# Note: for this demo to work properly, you'll need to install [statsmodels](http://http://statsmodels.sourceforge.net/)

# ## Import libraries

# In[1]:


import glob
import os
import numpy as np
import pandas as pd
import hypertools as hyp
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import statsmodels

get_ipython().run_line_magic('matplotlib', 'inline')


# ## Read in data

# In[2]:


results=pd.read_csv('data/temperatures.csv')
locs=pd.read_csv('data/temperature_locs.csv')


# ## Temperature dataframe

# In[3]:


results.head()


# ## Locations dataframe

# In[4]:


print(locs)


# ## Clean up NAs and convert to numpy array to pass into hyperplot

# In[5]:


results = results.dropna()
temps = results.as_matrix(locs['City'].as_matrix())
years = results.as_matrix(['Year'])
month = results.as_matrix(['Month'])


# ## Static 3D image: plot the high-dimensional data in a low dimensional space

# In[6]:


geo = hyp.plot(temps, group=years.flatten(), palette='RdBu_r', normalize='across')


# ## Static 2D image

# In[7]:


geo.plot(ndims=2)


# ## Color Bar

# In[8]:


fig = plt.figure(figsize=(8, 3))
ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
cmap = mpl.cm.RdBu_r
norm = mpl.colors.Normalize(vmin=1875, vmax=2013)
cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                norm=norm,
                                orientation='horizontal')
cb1.set_label('Years')
plt.show()


# ## Lowess predictions of PCA values by year

# In[9]:


sns.set_style('darkgrid')
sns.set_palette(palette='muted')
reduced_data = hyp.reduce(temps, reduce='PCA', ndims = 3)

results['PCA 1'] = reduced_data[:,0]
results['PCA 2'] = reduced_data[:,1]
results['PCA 3'] = reduced_data[:,2]

PCA1_df = results[['Year', 'PCA 1']]
PCA2_df = results[['Year', 'PCA 2']]
PCA3_df = results[['Year', 'PCA 3']]


# In[10]:


sns.regplot(x='Year', y='PCA 1', data=PCA1_df.groupby(['Year']).mean().reset_index(), lowess=True)
sns.regplot(x='Year', y='PCA 2', data=PCA2_df.groupby(['Year']).mean().reset_index(), lowess=True)
sns.regplot(x='Year', y='PCA 3', data=PCA3_df.groupby(['Year']).mean().reset_index(), lowess=True)
plt.show()


# ## Lowess predictions of PCA values by  average yearly temperature

# In[11]:


temp_PCA = pd.DataFrame()
temp_PCA['ave_temp'] = results.groupby(['Year']).mean()[locs['City']].mean(axis=1)


# In[12]:


temp_PCA = temp_PCA.join(PCA1_df.groupby(['Year']).mean(), how = 'outer')
temp_PCA = temp_PCA.join(PCA2_df.groupby(['Year']).mean(), how = 'outer')
temp_PCA = temp_PCA.join(PCA3_df.groupby(['Year']).mean(), how = 'outer')


# In[13]:


sns.regplot(x='ave_temp', y='PCA 1', data = temp_PCA, lowess=True)
plt.show()


# In[14]:


sns.regplot(x='ave_temp', y='PCA 2', data = temp_PCA, lowess=True)
plt.show()


# In[15]:


sns.regplot(x='ave_temp', y='PCA 3', data = temp_PCA, lowess=True)
plt.show()


# ## Linear regression predictions of PCA values by month

# In[16]:


PCA1_df = results[['Month', 'Year', 'PCA 1']]
PCA2_df = results[['Month', 'Year', 'PCA 2']]
PCA3_df = results[['Month', 'Year', 'PCA 3']]


# In[17]:


sns.regplot(x='Month', y='PCA 1', data=PCA1_df.groupby(['Month', 'Year']).mean().reset_index(), truncate = True, lowess=True)
sns.regplot(x='Month', y='PCA 2', data=PCA2_df.groupby(['Month', 'Year']).mean().reset_index(), truncate = True, lowess=True)
sns.regplot(x='Month', y='PCA 3', data=PCA3_df.groupby(['Month', 'Year']).mean().reset_index(), truncate = True, lowess=True)
plt.show()


# In[18]:


temps_locs = pd.DataFrame()
temps_locs = results.groupby(['Year']).mean()[locs['City']].reset_index()


# In[19]:


meltCov = pd.melt(temps_locs,id_vars=['Year'], var_name='Cities', value_name='Average Temperature')
sns.set(style="whitegrid")
sns.set_palette(palette='muted')
g = sns.lmplot(x = 'Year', y = 'Average Temperature', hue="Cities", data = meltCov, fit_reg=False, legend_out=True)
regplot = sns.regplot(x = 'Year', y = 'Average Temperature', data = meltCov, lowess = True, scatter=False, ax=g.axes[0, 0], color='k')
regplot.set(ylim=(0, 30), xlim=(1870,2040))
plt.show()


# In[ ]:




