from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class RunByRun(db.Model):
    
    run_id = db.Column('run_id', db.Integer, nullable=False, primary_key=True)
    
    weather_flag = db.Column('weather_flag', db.String, nullable=False)
    run_flag = db.Column('run_flag', db.String, nullable=False)

    tmin = db.Column('tmin', db.Float, nullable=False)
    tmax = db.Column('tmax', db.Float, nullable=False)
    wobble = db.Column('wobble', db.String, nullable=False)

    src_id = db.Column(db.Integer, db.ForeignKey("sources.src_id"), nullable=False)
    
    N_on = db.Column('N_on', db.Integer, nullable=False)
    N_off = db.Column('N_off', db.Integer, nullable=False)
    N_excess = db.Column('N_excess', db.Integer, nullable=True)
    alpha = db.Column('alpha', db.Float, nullable=True)
    sigma = db.Column('sigma', db.Float, nullable=True)

    exposure = db.Column('exposure', db.Float, nullable=False)
    livetime = db.Column('livetime', db.Float, nullable=True)
    deadtime = db.Column('deadtime', db.Float, nullable=True)
    
    pl_fit_flag = db.Column('pl_fit_flag', db.String, nullable=True)
    pl_index = db.Column('pl_index', db.Float, nullable=True)
    pl_index_err = db.Column('pl_index_err', db.Float, nullable=True)
    pl_amplitude = db.Column('pl_amplitude', db.Float, nullable=True)
    pl_amplitude_err = db.Column('pl_amplitude_err', db.Float, nullable=True)
    
    pl_e_min = db.Column('pl_e_min', db.Float, nullable=True)
    pl_e_max = db.Column('pl_e_max', db.Float, nullable=True)
    pl_e2dnde = db.Column('pl_e2dnde', db.Float, nullable=True)
    pl_e2dnde_err = db.Column('pl_e2dnde_err', db.Float, nullable=True)
    pl_e2dnde_errn = db.Column('pl_e2dnde_errn', db.Float, nullable=True)
    pl_e2dnde_errp = db.Column('pl_e2dnde_errp', db.Float, nullable=True)
    pl_e2dnde_ul = db.Column('pl_e2dnde_ul', db.Float, nullable=True)
    pl_is_ul = db.Column('pl_is_ul', db.Boolean, nullable=True)
    pl_stat = db.Column('pl_stat', db.Float, nullable=True)
    pl_ts = db.Column('pl_ts', db.Float, nullable=True)

    def __init__(self, run_id, src_id, tmin, tmax, N_on, N_off, N_excess, alpha, exposure, livetime, deadtime, sigma):
        self.run_id = run_id
        self.src_id = src_id
        self.tmin = tmin
        self.tmax = tmax
        self.N_on = N_on
        self.N_off = N_off
        self.N_excess = N_excess
        self.alpha = alpha
        self.exposure = exposure
        self.livetime = livetime
        self.deadtime = deadtime
        self.sigma = sigma
        
    def __repr__(self):
        return "<Run '%s', '%s', '%s', '%s', '%s', '%s'>" %(self.run_id, \
            self.src_id, self.weather_flag, self.run_flag, self.pl_fit_flag, self.sigma)

class Sources(db.Model):
    
    src_id = db.Column('src_id', db.Integer, nullable=False, primary_key=True)
    name = db.Column('name', db.String, nullable=False)
    ra = db.Column('ra', db.Float, nullable=False)
    dec = db.Column('dec', db.Float, nullable=False)
    N_on = db.Column('N_on', db.Float, nullable=True)
    N_off = db.Column('N_off', db.Float, nullable=True)
    alpha = db.Column('alpha', db.Float, nullable=True)
    sigma = db.Column('sigma', db.Float, nullable=True)
    exposure = db.Column('exposure', db.Float, nullable=True)
    runs = db.relationship("RunByRun", backref="src", lazy=True)
    
    def __init__(self, src_id, name, ra, dec, N_on, N_off, alpha, sigma, exposure):
        self.src_id = src_id
        self.name = name
        self.ra = ra
        self.dec = dec
        self.N_on = N_on
        self.N_off = N_off
        self.alpha = alpha
        self.sigma = sigma
        self.exposure = exposure

    def __repr__(self):
        return "<Sources '%s', '%s', '%s', '%s'>" %(self.src_id, self.name, self.ra, self.dec)

class Daily(db.Model):

    id_ = db.Column('id', db.Integer, nullable=False, primary_key=True)
    run_id = db.Column('run_id', db.Integer, nullable=False)
    event = db.Column('event', db.String, nullable=False)
    N_on = db.Column('N_on', db.Integer, nullable=False)
    N_off = db.Column('N_off', db.Integer, nullable=False)
    alpha = db.Column('alpha', db.Float, nullable=False)
    exposure = db.Column('exposure', db.Float, nullable=False)
    livetime = db.Column('livetime', db.Float, nullable=True)
    deadtime = db.Column('deadtime', db.Float, nullable=True)
    sigma = db.Column('sigma', db.Float, nullable=False)

    
    def __init__(self, id_, run_id, event):
        self.id = id_
        self.run_id = run_id
        self.event = event
        self.N_on = N_on
        self.N_off = N_off
        self.alpha = alpha
        self.exposure = exposure
        self.livetime = livetime
        self.deadtime = deadtime
        self.sigma = sigma
        
    def __repr__(self):
        return "<Run '%s', '%s', '%s', '%s', '%s', '%s'>" %(self.run_id, \
            self.event, self.N_on, self.N_off, self.alpha, self.sigma)

