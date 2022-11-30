from flask import Blueprint, request, render_template, send_from_directory, jsonify
from backend.models import RunByRun, Sources

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins
import numpy as np
import pandas as pd

from . import utils

from astropy.coordinates import SkyCoord
import astropy.units as u

import plotly.express as px

from pathlib import Path

public = Blueprint('public', __name__, url_prefix='/')

@public.route('/', methods=['GET', 'POST'])
def nextday_viewer():
	return render_template("index.html", token="test")

@public.route('/data/<path:filename>')
def image_static(filename):
    return send_from_directory('./data/', filename)

@public.route('/runs/', methods=['GET'])
def get_runs():
	rbr = RunByRun.query.all()
	runs = [get_related_attr(run.__dict__, run) for run in rbr]
	return jsonify({'data': runs})

@public.route('/run/<run_id>', methods=['GET'])
def get_run(run_id):
	rbr = RunByRun.query.filter_by(run_id=run_id).first()
	data = get_related_attr(rbr.__dict__, rbr)
	return jsonify({'data': data})

@public.route('/anasum/', methods=['GET'])
def get_anasum():
	args = request.args.to_dict()
	run_id = args["run"]
	base = f"/{run_id}/veritas/"
	full_filename = base+"/dataset.png"
	return render_template("anasum.html", user_image = full_filename)

@public.route('/fit/', methods=['GET'])
def get_fit():
	args = request.args.to_dict()
	run_id = args["run"]
	base = f"/{run_id}/veritas/"
	fit_filename = base+"/fit.png"
	sed_filename = base+"/sed.png"
	return render_template("fit.html", sed_image = sed_filename, fit_image=fit_filename)

@public.route('/main_plot/', methods=['GET'])
def get_main_plot():
	srcs = Sources.query.all()
	data = [[src.name, src.ra, src.dec, src.exposure, src.sigma] for src in srcs]
	data = np.asarray(data)
	events = list(set(data[:,0]))

	coord = SkyCoord(data[:,1], data[:,2], frame='icrs', unit=u.deg)

	evt_df = pd.DataFrame(index=range(len(data)))
	evt_df['exposure'] = ["{:.1f} hrs".format(float(t)) for t in data[:,3]]
	evt_df['sigma'] = ["{:.2f}".format(float(s)) for s in data[:,4]]
	evt_df['lat'] = coord.dec
	evt_df['lon'] = coord.ra.wrap_at('180d')
	evt_df['event'] = data[:,0]

	fig = px.scatter_geo(evt_df,lat="lat", lon="lon", hover_name="event", hover_data=["exposure", "sigma"], projection="aitoff")
	fig.update_geos(
	    visible=True,
	    framecolor="black",
	    framewidth=1,
	    landcolor="white",
	    countrywidth=0,
	    coastlinewidth=0,
	    lataxis_showgrid=True,
	    lonaxis_showgrid=True,
	)
	
	xtext = [r"{}&#176;".format(t) for t in np.arange(0, 361, step=30)]
	ytext = [r"{}&#176;".format(t) for t in np.arange(-80, 81, step=20) if t !=0]
	fig.add_scattergeo(lat=np.ones(18), lon=np.arange(0, 359, step=30),
		mode="text", text=xtext, textfont_size=8, hoverinfo="none", showlegend=False)
	fig.add_scattergeo(lat=[v for v in np.arange(-80, 81, step=20) if v!=0], lon=np.ones(9)*230,
		mode="text", text=ytext, textfont_size=8, hoverinfo="none", showlegend=False)

	return fig.to_html()
           
@public.route('/evt_plot/', methods=['GET'])
def get_evt_plot():
	args = request.args.to_dict()
	run_id = args["run"]
	src_id = args["src"]
	rbr = RunByRun.query.filter_by(src_id=src_id).all()
	data = [[run.run_id,
		run.sigma, 
		run.tmin, 
		run.pl_e2dnde, 
		run.pl_e2dnde_err,
		run.pl_e2dnde_ul, 
		run.pl_is_ul] for run in rbr]
	data = np.asarray(data).astype("float")
	data = np.nan_to_num(data)

	fig, ax = plt.subplots(1, 3, figsize=(10, 3))

	valid_ul = (data[:,6]>0)*(data[:,5] > 0)

	valid_flx = (data[:,1]>0)*(data[:,3]>0)*(data[:,6]==0)

	fdf = pd.DataFrame(index=range(sum(valid_ul+valid_flx)))
	fdf['Sigma'] = data[:,1][valid_ul+valid_flx]
	fdf['flux'] = data[:,3][valid_ul+valid_flx]
	fdf['flux_err'] = data[:,4][valid_ul+valid_flx]
	fdf['flux_ul'] = data[:,5][valid_ul+valid_flx]

	flabels = []
	fpnts = []
	j = 0
	for i, d in enumerate(data):
	    if valid_flx[i] or valid_ul[i]:
	        label = fdf.iloc[[j], :].T
	        label.columns = [str(int(d[0]))]

	        # .to_html() is unicode; so make leading 'u' go away with str()
	        flabels.append(str(label.to_html()))
	        if valid_flx[i]:
	            fpnts.append(d[3])
	        else:
	            fpnts.append(d[5])
	        j+=1

	yerr = np.log10(data[:,3][valid_flx]+data[:,4][valid_flx])-np.log10(data[:,3][valid_flx])
	
	temp = ax[0].errorbar(data[:,2][valid_flx], np.log10(data[:,3][valid_flx]), yerr=yerr, marker="o", ls="")
	c = temp.get_children()[0].get_color()
	ax[0].errorbar(data[:,2][valid_ul], np.log10(data[:,5][valid_ul]), yerr=0.2, uplims=True, marker="o", ls="", color=c)
	
	
	fpoints = ax[0].plot(data[:,2][valid_flx+valid_ul], np.log10(fpnts), marker="o", c=c, zorder=10, ls="")
	
	ax[0].set_xlim(min(data[:,2])-10, max(data[:,2])+10)
	crab = np.log10(utils.crab_flux)
	ax[0].plot([min(data[:,2])-10, max(data[:,2])+10], [crab, crab], color="r", ls=":")
	ax[0].plot([min(data[:,2])-10, max(data[:,2])+10], [crab-1,crab-1], color="r", ls=":")
	ax[0].plot([min(data[:,2])-10, max(data[:,2])+10], [crab-2,crab-2], color="r", ls=":")
	ax[0].plot([min(data[:,2])-10, max(data[:,2])+10], [crab-3,crab-3], color="r", ls=":")
	
	ax[0].text(max(data[:,2]+9), crab-3.2, "0.1% of Crab", ha="right", color="r")
	ax[0].text(max(data[:,2]+9), crab-2.2, "1% of Crab", ha="right", color="r")
	ax[0].text(max(data[:,2]+9), crab-1.2, "10% of Crab", ha="right", color="r")
	ax[0].text(max(data[:,2]+9), crab-0.2, "Crab flux", ha="right", color="r")
	ax[0].set_xlabel("Run start time [MJD]")
	ax[0].set_ylabel("log(Energy flux) [TeV/cm^2/s]")
	
	points = ax[1].plot(data[:,2], data[:,1], marker="o", ls="")
	ax[1].plot([min(data[:,2])-10, max(data[:,2])+10], [0,0], color="r", ls=":")
	ax[1].set_xlabel("Run start time [MJD]")
	ax[1].set_ylabel("Significance")
	ax[1].set_xlim(min(data[:,2])-10, max(data[:,2])+10)
	
	data = [[run.N_on, 
	    run.N_off, 
	    run.alpha,
	    run.exposure,
	    run.run_id,
	    run.sigma,
	    run.tmin] for run in rbr]
	data = np.array(data)

	Non = data[:,0].cumsum()
	Noff = data[:,1].cumsum()
	alpha = [np.average(data[:,2][:i+1], weights=data[:,3][:i+1]) for i in range(len(data))]
	exp = list(data[:,3].cumsum()/60)

	sigma = [utils.LiMaSiginficance(on, off, a) for on, off, a in zip(Non, Noff, alpha)]

	df = pd.DataFrame(index=range(len(data)))
	df['Sigma'] = ["{:.3f}".format(float(s)) for s in np.nan_to_num(data[:,5].astype("float"))]
	df['Exposure'] = ["{:.1f}".format(float(t)/60) for t in np.nan_to_num(data[:,3]).astype("float")]

	labels = []
	for i, d in enumerate(data):
	    label = df.iloc[[i], :].T
	    label.columns = [str(int(d[4]))]

	    # .to_html() is unicode; so make leading 'u' go away with str()
	    labels.append(str(label.to_html()))

	points_cum = ax[2].plot(exp, sigma, marker="o")
	ax[2].set_xlabel("Exposure time [minutes]")
	ax[2].set_ylabel("Cumulative sigma")
	
	ftooltip = plugins.PointHTMLTooltip(fpoints[0], flabels, voffset=10, hoffset=10, css=utils.table_css)
	plugins.connect(fig, ftooltip)

	tooltip = plugins.PointHTMLTooltip(points[0], labels, voffset=10, hoffset=10, css=utils.table_css)
	plugins.connect(fig, tooltip)

	tooltip = plugins.PointHTMLTooltip(points_cum[0], labels, voffset=10, hoffset=10, css=utils.table_css)
	plugins.connect(fig, tooltip)
	plt.tight_layout()
	
	return mpld3.fig_to_html(fig)

def get_related_attr(d, r):
	output = {comp: d[comp] for comp in d if comp != '_sa_instance_state' and comp!='src'}
	output['tmin'] = utils.MJD2UTC(output["tmin"])
	output['tmax'] = utils.MJD2UTC(output["tmax"])
	output['event'] = r.src.name
	output['ra'] = r.src.ra
	output['dec'] = r.src.dec
	return output
