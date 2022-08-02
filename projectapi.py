from fastapi import FastAPI, Request, HTTPException, Body
from starlette.responses import FileResponse
import psycopg2 as pg
from models import SampleIC, PFMdata
import matplotlib.pyplot as plt
from scipy import stats
import uvicorn

app = FastAPI()

@app.put("/putSampleICData")
async def put_sample_data(request: Request, sample_model: SampleIC = Body(..., alias='sampleModel')):
    print(sample_model)
    try:
        host = "localhost"
        database = "Project"
        user = "postgres"
        password = "password"
        port = 5432
        conn = None
        cur = None
        conn = pg.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port)
        cur = conn.cursor()
        cur.execute("""select * from public.sample_ic where sample_id ='"""+sample_model.sampleId+"""'""")
        sample_db_data = cur.fetchall()
        if sample_db_data:
            cur.execute("""update public.sample_ic set bridge_ic ="""+str(sample_model.bridgeIc)+""" , bridge_width = """+
                        str(sample_model.bridgeWidth)+""" , full_width_ic = """+str(sample_model.fullWidthIc)+""" where sample_id ='"""+sample_model.sampleId+"""'""")

        else:
            cur.execute("""insert into public.sample_ic values (%s, %s, %s, %s)""", (sample_model.sampleId, sample_model.bridgeIc, sample_model.bridgeWidth, sample_model.fullWidthIc))

        cur.execute("""select * from public.sample_pfm where sample_id ='"""+sample_model.sampleId+"""'""")
        sample_pfm_db_data = cur.fetchall()
        if sample_pfm_db_data:
            cur.execute("""update public.sample_pfm set average = """+str(sample_model.average)+""" where sample_id ='"""+sample_model.sampleId+"""'""")
        else:
            cur.execute("""insert into public.sample_pfm values (%s, %s)""", (sample_model.sampleId, sample_model.average))
        conn.commit()
        return [sample_model]

    except Exception as error:
        print(str(error))
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()

@app.put("/PredictIC")
async def PredictIC(request: Request, PFM_To_Estimate_IC: float):
    try:
        host = "localhost"
        database = "Project"
        user = "postgres"
        password = "password"
        port = 5432
        conn = None
        cur = None
        conn = pg.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port)
        cur = conn.cursor()
        cur.execute(
            "select average from sample_pfm inner join sample_ic on sample_pfm.sample_id=sample_ic.sample_id where average is not null and full_width_ic is not null")
        a = cur.fetchall()
        cur.execute(
            "select full_width_ic from sample_pfm inner join sample_ic on sample_pfm.sample_id=sample_ic.sample_id where average is not null and full_width_ic is not null")
        b = cur.fetchall()
        average = []
        IC = []

        for i in a:
            for j in i:
                average.append(j)

        for i in b:
            for j in i:
                IC.append(j)


        conn.commit()

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()

    slope, intercept, r, p, std_err = stats.linregress(average, IC)

    def myfunc(average):
        return slope * average + intercept
    predict = myfunc(PFM_To_Estimate_IC)

    return {"Sample IC Estimate": predict}



@app.get("/sampleICData")
async def get_sample_data(request: Request):
    try:
        host = "localhost"
        database = "Project"
        user = "postgres"
        password = "password"
        port = 5432
        conn = None
        cur = None
        conn = pg.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port)
        cur = conn.cursor()
        cur.execute("""select ic.sample_id, bridge_ic, bridge_width, 
                    full_width_ic, average from
                    public.sample_ic ic, public.sample_pfm pfm
                    where ic.sample_id = pfm.sample_id""")
        data = cur.fetchall()
        columns = [col[0] for col in cur.description]
        result = [dict(zip(columns, rec)) for rec in data]
        sample_list = []
        for rec in result:
            sample = SampleIC()
            sample.sampleId = rec['sample_id']
            sample.average = rec['average']
            sample.bridgeIc = rec['bridge_ic']
            sample.fullWidthIc = rec['full_width_ic']
            sample.bridgeWidth = rec['bridge_width']
            sample_list.append(sample)

        return sample_list
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()

def get_sample_values():
    host = "localhost"
    database = "Project"
    user = "postgres"
    password = "password"
    port = 5432
    conn = None
    cur = None

    try:
        conn = pg.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port)

        cur = conn.cursor()
        cur.execute(
            "select average from sample_pfm inner join sample_ic on sample_pfm.sample_id=sample_ic.sample_id where average is not null and full_width_ic is not null")
        a = cur.fetchall()
        cur.execute(
            "select full_width_ic from sample_pfm inner join sample_ic on sample_pfm.sample_id=sample_ic.sample_id where average is not null and full_width_ic is not null")
        b = cur.fetchall()
        average = []
        IC = []

        for i in a:
            for j in i:
                average.append(j)

        for i in b:
            for j in i:
                IC.append(j)

        conn.commit()
    except Exception as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()

    slope, intercept, r, p, std_err = stats.linregress(average, IC)

    def myfunc(average):
        return slope * average + intercept

    mymodel = list(map(myfunc, average))

    return slope, intercept, average, mymodel, IC


@app.get("/ICDistributionPlot")
async def get_sample_ic_distribution_plot():
    try:
        slope, intercept, average, mymodel, IC = get_sample_values()
        plt.switch_backend('Agg')
        plt.xlabel("IC values")
        plt.plot(IC, color="blue", marker="o")
        plt.savefig('/SuperConductorSample/static/sample_ic_distribution.png')
        return FileResponse('/SuperConductorSample/static/sample_ic_distribution.png')
    except Exception as error:
        return {"error": str(error)}

@app.get("/PFMDistributionPlot")
async def get_sample_pfm_distribution_plot():
    try:
        slope, intercept, average, mymodel, IC = get_sample_values()
        plt.switch_backend('Agg')
        plt.plot(average, color="red", marker="+")
        plt.xlabel("Averages")
        plt.savefig('/SuperConductorSample/static/sample_pfm_avg_distribution.png')
        return FileResponse('/SuperConductorSample/static/sample_pfm_avg_distribution.png')
    except Exception as error:
        return {"error": str(error)}

@app.get("/LinearGraph_IC_PFM")
async def get_LinearGraph_IC_PFM():
    try:
        slope, intercept, average, mymodel, IC = get_sample_values()
        plt.switch_backend('Agg')
        plt.xlabel('Averages')
        plt.ylabel("IC values")
        plt.scatter(average, IC, color="red", marker="+")
        plt.plot(average, mymodel)
        plt.savefig('/SuperConductorSample/static/scatter_avg_ic.png')
        return FileResponse('/SuperConductorSample/static/scatter_avg_ic.png')
    except Exception as error:
        return {"error": str(error)}

@app.get("/IC_barchat")
async def get_IC_barchart():
    try:
        slope, intercept, average, mymodel, IC = get_sample_values()
        plt.switch_backend('Agg')
        plt.bar(average, IC, width=0.3)
        plt.savefig('/SuperConductorSample/static/bar_avg_ic.png')
        return FileResponse('/SuperConductorSample/static/bar_avg_ic.png')
    except Exception as error:
        return {"error": str(error)}

@app.get("/PFM_Histogram")
async def get_PFM_Histogram():
    try:
        slope, intercept, average, mymodel, IC = get_sample_values()
        plt.switch_backend('Agg')
        plt.hist(average, width=0.5)  # hist_average
        plt.savefig('/SuperConductorSample/static/hist_avg.png')
        return FileResponse('/SuperConductorSample/static/hist_avg.png')
    except Exception as error:
        return {"error": str(error)}

@app.get("/IC_Histogram")
async def get_IC_Histogram():
    try:
        slope, intercept, average, mymodel, IC = get_sample_values()
        plt.switch_backend('Agg')
        plt.hist(IC)  # hist_ic
        plt.savefig('/SuperConductorSample/static/hist_ic.png')
        return FileResponse('/SuperConductorSample/static/hist_ic.png')
    except Exception as error:
        return {"error": str(error)}


uvicorn.run(app, host="0.0.0.0", port=8000)