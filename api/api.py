from flask import Flask, request
import util

app = Flask(__name__)

@app.route("/")
def api_index():
    return 400

@app.route("/energetic/mass", methods = ['POST'])
def energetic_raw_massc():

    if not request.json:
        return "JSON Request Malformed", 400
    
    data = request.json

    error, code = util.verify_MassParam(data)
    if error:
        return error, code

    energetic_mass = data[0]
    wet_mass = data[1]
    dry_mass = data[2]

    calculation = util.energetic_mass_calculation(energetic_mass=energetic_mass, wet_mass=wet_mass, dry_mass=dry_mass)
    return {"result": calculation}

@app.route("/energetic/rcm", methods = ['POST'])
def energetic_rcm_massc():

    if not request.json:
        return "JSON Request Malformed", 400
    
    data = request.json

    error, code = util.verify_RCMParams(data)
    if error:
        return error, code

    calculation = util.energetic_rcm_calculation(data)
    return {"result": calculation}

@app.route("/energetic/sim", methods = ['POST'])
def energetic_sim():

    if not request.json:
        return "JSON Request Malformed", 400
    
    data = request.json
    error, code = util.verify_ESimData(data)
    if error:
        return error, code

    payload = {
        "name": data["name"],
        "sims": []
    }
    calculation = util.energetic_sim(data)
    for calc in calculation:
        payload["sims"].append({
            "efficiency": calc.efficiency,
            "result": calc.result()
        })
    return payload

@app.route("/energetic/sim", methods = ['POST'])
def energetic_sim():

    if not request.json:
        return "JSON Request Malformed", 400
    
    data = request.json
    error, code = util.verify_ESimData(data)
    if error:
        return error, code

    payload = {
        "name": data["name"],
        "sims": []
    }
    calculation = util.energetic_sim(data)
    for calc in calculation:
        payload["sims"].append({
            "efficiency": calc.efficiency,
            "result": calc.result()
        })
    return payload

if __name__ == "__main__":
    app.run(debug=True)