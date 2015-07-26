import MySQLdb

__author__ = 'antonior'

class GelMySql():
    def __init__(self,  db_name, pwd="pa55w0rd"):

        self.db_name = db_name
        self.db = MySQLdb.connect("10.0.32.42","pipeline",pwd,self.db_name)
        self.cursor = self.db.cursor()

    def execute(self, query):
        self.cursor.execute(query)

    def get_cancer_samples(self):
        self.execute("select sample_ids.participant_id,  samples.well_id, samples.gel_id,samples.type, sample_types.type, modifier, center_patient_id, CENTER, pilot, TUMOR, gender from samples, sample_types, patients, sample_ids where samples.gel_id = patients.gel_id and samples.type = sample_types.id and sample_ids.gel_id = samples.gel_id ;")
        row = self.cursor.fetchone()
        while row is not None:
            field_names = [i[0] for i in self.cursor.description]
            data = {key: value for key, value in zip(field_names, row)}
            yield data
            row = self.cursor.fetchone()

    def get_LP(self, id):
        self.execute('SELECT well_id FROM gel_RD.sample_ids where participant_id="'+str(id)+'";')
        row = self.cursor.fetchone()
        field_names = [i[0] for i in self.cursor.description]
        data = {key: value for key, value in zip(field_names, row)}
        return data["well_id"]

