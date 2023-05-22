from odoo import models, fields, api, _

class kb_mrp_sawmil_report(models.Model):
    _name = 'kb.mrp.sawmil.report'

    name = fields.Char(string="Name")
    kb_mrp_sawmill_report_ids = fields.One2many('kb.mrp.sawmil.report.line', 'kb_mrp_sawmil_report_id')


class kb_mrp_sawmil_report_line(models.Model):
    _name = 'kb.mrp.sawmil.report.line'

    kb_mrp_sawmil_report_id = fields.Many2one('kb.mrp.sawmil.report')
    name_header = fields.Char(string='Name Header', default="New")
    tanggal_gesek = fields.Date(string="Tanggal gesek")
    keterangan = fields.Text(string="Keterangan")
    name_line = fields.Char(string='Name Line', default="New")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang_line = fields.Float(string="Panjang Line")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    name_detail = fields.Char(string="Name Detail", default="New")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang_detail = fields.Float(string="Panjang Detail")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    kb_mrp_sawmil_id = fields.Many2one('kb.mrp.sawmil', string="No Proses")
    kb_mrp_sawmil_line_id = fields.Many2one('kb.mrp.sawmil.line', string="Kb Mrp Sawmil Line Id")
    kb_mrp_sawmil_line_detail_id = fields.Many2one('kb.mrp.sawmil.line.detail', string="Kb Mrp Sawmil Line Id")



class kb_mrp_vakum_celup_report(models.Model):
    _name = 'kb.mrp.vakum.celup.report'

    name = fields.Char(string="Name")
    kb_mrp_vakum_celup_report_ids = fields.One2many('kb.mrp.vakum.celup.report.line', 'vakum_celup_report_id')


class kb_mrp_vakum_celup_report_line(models.Model):
    _name = 'kb.mrp.vakum.celup.report.line'

    vakum_celup_report_id = fields.Many2one('kb.mrp.vakum.celup.report')
    name_header = fields.Char(string='Name Header', default="New")
    tanggal_selesai_vakum = fields.Date(string="Tanggal Selesai Vakum")
    keterangan = fields.Text(string="Keterangan")
    name_line = fields.Char(string='Name Line', default="New")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang_line = fields.Float(string="Panjang Line")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    name_detail = fields.Char(string="Name Detail", default="New")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang_detail = fields.Float(string="Panjang Detail")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    vakum_celup = fields.Selection([('vakum', 'Vakum'), ('celup', 'Celup'), ('vakum_&_celup', 'Vakum & Celup'),
                                    ('tidak_sama_sekali', 'Tidak Sama Sekali')])
    kb_mrp_vakum_celup_id = fields.Many2one('kb.mrp.vakum.celup', string="No Proses")
    kb_mrp_vakum_celup_line_id = fields.Many2one('kb.mrp.vakum.celup.line', string="Kb Mrp Vakum Celup Line Id")
    kb_mrp_vakum_celup_line_detail_id = fields.Many2one('kb.mrp.vakum.celup.line.detail', string="Kb Mrp Vakum Celup Line Id")

class kb_mrp_sticking_report(models.Model):
    _name = 'kb.mrp.sticking.report'

    name = fields.Char(string="Name")
    kb_mrp_sticking_report_ids = fields.One2many('kb.mrp.sticking.report.line', 'sticking_report_id')


class kb_mrp_sticking_report_line(models.Model):
    _name = 'kb.mrp.sticking.report.line'

    sticking_report_id = fields.Many2one('kb.mrp.sticking.report')
    name_header = fields.Char(string='Name Header', default="New")
    tanggal_selesai_vakum = fields.Date(string="Tanggal Selesai Vakum")
    tanggal_selesai_stick = fields.Date(string="Tanggal Selesai Stick")
    keterangan = fields.Text(string="Keterangan")
    name_line = fields.Char(string='Name Line', default="New")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang_line = fields.Float(string="Panjang Line")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    name_detail = fields.Char(string="Name Detail", default="New")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang_detail = fields.Float(string="Panjang Detail")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    kb_mrp_sticking_id = fields.Many2one('kb.mrp.sticking', string="No")
    kb_mrp_sticking_line_id = fields.Many2one('kb.mrp.sticking.line', string="Kb Mrp Sticking Line Id")
    kb_mrp_sticking_line_detail_id = fields.Many2one('kb.mrp.sticking.line.detail', string="Kb Mrp Sticking Line Id")

class kb_mrp_oven_report(models.Model):
    _name = 'kb.mrp.oven.report'

    name = fields.Char(string="Name")
    kb_mrp_oven_report_ids = fields.One2many('kb.mrp.oven.report.line', 'oven_report_id')

class kb_mrp_oven_report_line(models.Model):
    _name = 'kb.mrp.oven.report.line'

    oven_report_id = fields.Many2one('kb.mrp.oven.report')
    name_header = fields.Char(string='Name Header', default="New")
    tanggal_masuk_oven = fields.Date(string="Tanggal Masuk Oven")
    tanggal_selesai_vakum = fields.Date(string="Tanggal Selesai Vakum")
    tanggal_selesai_stick = fields.Date(string="Tanggal Selesai Stick")
    tanggal_keluar_oven = fields.Date(string="Tanggal Keluar Oven")
    keterangan = fields.Text(string="Keterangan")
    name_line = fields.Char(string='Name Line', default="New")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang_line = fields.Float(string="Panjang Line")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    name_detail = fields.Char(string="Name Detail", default="New")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang_detail = fields.Float(string="Panjang Detail")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    vakum_celup = fields.Selection([('vakum', 'Vakum'), ('celup', 'Celup'), ('vakum_&_celup', 'Vakum & Celup'),
                                    ('tidak_sama_sekali', 'Tidak Sama Sekali')])
    kb_mrp_oven_id = fields.Many2one('kb.mrp.oven', string="No")
    kb_mrp_oven_line_id = fields.Many2one('kb.mrp.oven.line', string="Kb Mrp Oven Line Id")
    kb_mrp_oven_line_detail_id = fields.Many2one('kb.mrp.oven.line.detail', string="Kb Mrp Oven Line Id")


class kb_mrp_gudang_kering_report(models.Model):
    _name = 'kb.mrp.gudang.kering.report'

    name = fields.Char(string="Name")
    kb_mrp_gudang_kering_report_ids = fields.One2many('kb.mrp.gudang.kering.report.line', 'gudang_kering_report_id')


class kb_mrp_gudang_kering_report_line(models.Model):
    _name = 'kb.mrp.gudang.kering.report.line'

    gudang_kering_report_id = fields.Many2one('kb.mrp.gudang.kering.report')
    name_header = fields.Char(string='Name Header', default="New")
    tanggal_selesai_stick = fields.Date(string="Tanggal Selesai Stick")
    tanggal_masuk_oven = fields.Date(string="Tanggal Masuk Oven")
    tanggal_keluar_oven = fields.Date(string="Tanggal Keluar Oven")
    tanggal_in_gd = fields.Date(string="Tanggal In GD")
    tanggal_out_gd = fields.Date(string="Tanggal Out GD")
    keterangan = fields.Text(string="Keterangan")
    name_line = fields.Char(string='Name Line', default="New")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang_line = fields.Float(string="Panjang Line")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    no_chamber = fields.Float(string="No Chamber")
    name_detail = fields.Char(string="Name Detail", default="New")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang_detail = fields.Float(string="Panjang Detail")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    vakum_celup = fields.Char(string="Vakum / Celup")
    kb_mrp_gudang_kering_id = fields.Many2one('kb.mrp.gudang.kering', string="No")
    kb_mrp_gudang_kering_line_id = fields.Many2one('kb.mrp.gudang.kering.line', string="Kb Mrp Gudang Kering Line Id")
    kb_mrp_gudang_kering_line_detail_id = fields.Many2one('kb.mrp.gudang.kering.line.detail', string="Kb Mrp Gudang Kering Line Id")













#