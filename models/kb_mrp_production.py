from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError
from collections import defaultdict

import xlrd
import base64
import os

class kb_mrp_pembahanan(models.Model):
    _name = 'kb.mrp.pembahanan'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_pembahanan, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.pembahanan') or '/'
                rec.name = seq
        return res


    name = fields.Char(string='No', default="New")
    tahun = fields.Char(string="Tahun")
    tanggal_masuk_oven = fields.Date(string="Tanggal Masuk Oven")
    tanggal_selesai_vakum = fields.Date(string="Tanggal Selesai Vakum")
    tanggal_selesai_stick = fields.Date(string="Tanggal Selesai Stick")
    item = fields.Many2one('product.product', string="Item")
    code = fields.Char(string="Code")
    tebal = fields.Float(string="Tebal")
    pcs = fields.Float(string="PCS")
    m3 = fields.Float(string="M3")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    no_chamber = fields.Char(string="No Chamber")
    tanggal_keluar_oven = fields.Date(string="Tanggal Keluar Oven")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    vakum_celup = fields.Selection([('vakum','Vakum'),('celup','Celup')])
    shift = fields.Char(string="Shift")
    keterangan = fields.Text(string="Keterangan")

class kb_mrp_sawmil(models.Model):
    _name = 'kb.mrp.sawmil'

    def funct_print_excel_sawmil(self):
        context = self._context.copy()
        active_ids = context.get('active_ids', [])
        active_ids.append(0)
        active_ids.append(0)
        new_report_sawmil = self.env['kb.mrp.sawmil.report'].sudo().create({'name': 'New'})
        self._cr.execute("""(select
                                c.id as id_sawmil,
                                c.name as name_sawmil,
                                c.tanggal_gesek as tanggal_gesek_sawmil,
                                c.keterangan as keterangan_sawmil,
                                b.id as id_sawmil_line,
                                b.name as name_sawmil_line,
                                b.jenis_kayu as jenis_kayu_sawmil_line,
                                b.kode as kode_sawmil_line,
                                b.diameter1 as diameter1_sawmil_line,
                                b.diameter2 as diameter2_sawmil_line,
                                b.panjang as panjang_sawmil_line,
                                b.log_pakai_pcs as log_pakai_pcs_sawmil_line,
                                b.log_pakai_m3 as log_pakai_m3_sawmil_line,
                                a.id as id_sawmil_detail,
                                a.name as name_sawmil_detail,
                                a.tebal as tebal_sawmil_detail,
                                a.lebar as lebar_sawmil_detail,
                                a.panjang as panjang_sawmil_detail,
                                a.hasil_keping as hasil_keping_sawmil_detail,
                                a.hasil_m3 as hasil_m3_sawmil_detail,
                                a.shift as shift_sawmil_detail
                            from kb_mrp_sawmil_line_detail a
                            join kb_mrp_sawmil_line b on b.id = a.kb_mrp_sawmil_line_id 
                            join kb_mrp_sawmil c on c.id = b.kb_mrp_sawmil_id 
                            where c.id in {_sawmil}
                            order by c.id, b.id, a.id asc)""".format(_sawmil=tuple(active_ids)))
        dict_sawmil = self._cr.dictfetchall()
        if len(dict_sawmil) > 0:
            ins_values = ",".join([u"({},'{}','{}','{}',{},'{}','{}','{}',{},{},{},{},{},{},'{}',{},{},{},{},{},'{}',{},{})".format(
                data['id_sawmil'] or 'Null',
                data['name_sawmil'] or '',
                data['tanggal_gesek_sawmil'] or 'Null',
                data['keterangan_sawmil'] or '',
                data['id_sawmil_line'] or 'Null',
                data['name_sawmil_line'] or '',
                data['jenis_kayu_sawmil_line'] or '',
                data['kode_sawmil_line'] or '',
                data['diameter1_sawmil_line'] or 0,
                data['diameter2_sawmil_line'] or 0,
                data['panjang_sawmil_line'] or 0,
                data['log_pakai_pcs_sawmil_line'] or 0,
                data['log_pakai_m3_sawmil_line'] or 0,
                data['id_sawmil_detail'] or 'Null',
                data['name_sawmil_detail'] or '',
                data['tebal_sawmil_detail'] or 0,
                data['lebar_sawmil_detail'] or 0,
                data['panjang_sawmil_detail'] or 0,
                data['hasil_keping_sawmil_detail'] or 0,
                data['hasil_m3_sawmil_detail'] or 0,
                data['shift_sawmil_detail'] or '',
                self._uid,
                new_report_sawmil.id,
            ) for data in dict_sawmil])
            insert_query = u"insert into kb_mrp_sawmil_report_line (kb_mrp_sawmil_id,name_header,tanggal_gesek,keterangan," \
                           u"kb_mrp_sawmil_line_id,name_line,jenis_kayu,kode,diameter1,diameter2,panjang_line,log_pakai_pcs," \
                           u"log_pakai_m3,kb_mrp_sawmil_line_detail_id,name_detail,tebal,lebar,panjang_detail,hasil_keping," \
                           u"hasil_m3,shift,create_uid,kb_mrp_sawmil_report_id) values {_values}".format(_values=ins_values)
            self._cr.execute(insert_query)
            self._cr.commit()
            return {
                'type': 'ir.actions.act_url',
                'url': '/kb_mrp_sawmil_report/%s' % (new_report_sawmil.id),
                'target': 'new',
            }

    @api.model
    def create(self, vals):
        res = super(kb_mrp_sawmil, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.sawmil') or '/'
                rec.name = seq
        return res

    def func_process(self):
        if self.status == 'draft':
            self.status = 'process'
            for line in self.kb_mrp_sawmil_ids:
                line.status = 'process'

    def func_done(self):
        if self.status == 'process':
            self.status = 'done'
            for line in self.kb_mrp_sawmil_ids:
                line.status = 'done'
                line.location_id = self.location_dest_id
                update_query = "update kb_mrp_sawmil_line_detail set status = 'done'," \
                               "location_id = {_loc} where kb_mrp_sawmil_line_id = {_id}".format(_loc=self.location_dest_id.id, _id=line.id)
                self._cr.execute(update_query)
                self._cr.commit()
                for detail in line.kb_mrp_sawmil_line_ids:
                    check_sq = self.env['stock.quant'].sudo().search([('product_id', '=', detail.product_id.id), ('location_id', '=', detail.location_id.id)], limit=1)
                    if check_sq:
                        if check_sq.quantity < 0:
                            check_sq.quantity = detail.hasil_m3
                        else:
                            check_sq.quantity += detail.hasil_m3
                    else:
                        if detail.product_id.company_id.id != False:
                            company = detail.product_id.company_id.id
                        else:
                            company = None
                        vals = {
                            'product_id': detail.product_id.id,
                            'location_id': detail.location_id.id,
                            'quantity': detail.hasil_m3,
                            'company_id': company,
                        }
                        new_stock_quant = self.env['stock.quant'].sudo().create(vals)
        return True

    def func_view_mo(self):
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id('mrp.mrp_production_form_view')
        return {
            'name': 'Manufacturing Order',
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'views': [[form_view_id, 'form']],
            'res_id': self.mo_id.id,
        }


    def get_sawmil_detail_helper_ids(self):
        for this in self:
            self._cr.execute("""(select a.id from kb_mrp_sawmil_line_detail a
                                join kb_mrp_sawmil_line b on b.id = a.kb_mrp_sawmil_line_id 
                                join kb_mrp_sawmil c on c.id = b.kb_mrp_sawmil_id 
                                where c.id = {_id} and tag_card = true
                                order by a.name asc)""".format(_id=this.id))
            fet = [x[0] for x in self._cr.fetchall()]
            if len(fet) > 0:
                detail = self.env['kb.mrp.sawmil.line.detail'].browse(fet)
                this.sawmil_detail_helper_ids = detail.ids
            else:
                this.sawmil_detail_helper_ids = None


    tanggal_gesek = fields.Date(string="Tanggal gesek")
    name = fields.Char(string='No Sawmil', default="New")
    mo_id = fields.Many2one('mrp.production', string="No MO")
    status = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('done', 'Done')], default='draft')
    keterangan = fields.Text(string="Keterangan")
    kb_mrp_sawmil_ids = fields.One2many('kb.mrp.sawmil.line', 'kb_mrp_sawmil_id', string="Kb Mrp Sawmil Ids")
    location_dest_id = fields.Many2one('stock.location', string="Lokasi Tujuan")
    sawmil_detail_helper_ids = fields.One2many('kb.mrp.sawmil.line.detail', string="Sawmil Detail Helper", compute=get_sawmil_detail_helper_ids)


class kb_mrp_sawmil_line(models.Model):
    _name = 'kb.mrp.sawmil.line'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_sawmil_line, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.sawmil.line') or '/'
                rec.name = seq
        return res

    def func_line_detail(self):
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id('kb_mrp_production.kb_mrp_sawmil_line_id')
        return {
            'name': 'Detail',
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'kb.mrp.sawmil.line',
            'views': [[form_view_id, 'form']],
            'target': 'new',
            'res_id': self.id,
        }

    def func_ok(self):
        pass

    # @api.onchange('status')
    # def func_onchange_status(self):
    #     print("check", self.status)
    #     if self.status == 'done':
    #         for detail in self.kb_mrp_sawmil_line_ids:
    #             detail.location_id = self.location_id


    name = fields.Char(string="No Sawmil Line", default="New")
    kb_mrp_sawmil_id = fields.Many2one('kb.mrp.sawmil', string="No Proses")
    product_id = fields.Many2one('product.product', string="Product")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang = fields.Float(string="Panjang")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    nama_sawmil = fields.Char(string="Nomor Sawmil")
    nama_line = fields.Char(string="Nomor Line")
    location_id = fields.Many2one('stock.location', string="Lokasi Tujuan")
    status = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('done', 'Done')], default='draft')
    kb_mrp_sawmil_line_ids = fields.One2many('kb.mrp.sawmil.line.detail', 'kb_mrp_sawmil_line_id', string="Kb Mrp Sawmil Line Detail Ids")


class kb_mrp_sawmil_line_detail(models.Model):
    _name = 'kb.mrp.sawmil.line.detail'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_sawmil_line_detail, self).create(vals)
        for rec in res:
            if rec.kb_mrp_sawmil_line_id.status != 'done':
                if rec.name == "New":
                    seq = self.env['ir.sequence'].next_by_code('kb.mrp.sawmil.line.detail') or '/'
                    rec.name = seq
            else:
                raise ValidationError(_('You can not add a line, because the status has done!'))
        return res

    @api.onchange('status')
    def func_onchange_status(self):
        print("check", self.status)
        if self.status == 'done':
            self.location_id = self.kb_mrp_sawmil_line_id.location_id.id


    name = fields.Char(string="No Detail Sawmil", default="New")
    kb_mrp_sawmil_line_id = fields.Many2one('kb.mrp.sawmil.line', string="Kb Mrp Sawmil Line Id")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    product_id = fields.Many2one('product.product', string="Product")
    panjang = fields.Float(string="Panjang")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    status = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('done', 'Done')], default='draft')
    location_id = fields.Many2one('stock.location', string="Location Id")
    tag_card = fields.Boolean(string="Tag Card", default=False)

class kb_mrp_vakum_celup(models.Model):
    _name = 'kb.mrp.vakum.celup'


    def funct_print_excel_vakum_celup(self):
        context = self._context.copy()
        active_ids = context.get('active_ids', [])
        active_ids.append(0)
        active_ids.append(0)
        new_report_vakum_celup = self.env['kb.mrp.vakum.celup.report'].sudo().create({'name': 'New'})
        self._cr.execute("""(select
                                c.id as id_vakum,
                                c.name as name_vakum,
                                c.tanggal_selesai_vakum as tanggal_selesai_vakum,
                                c.keterangan as keterangan_vakum,
                                b.id as id_vakum_line,
                                b.name as name_vakum_line,
                                b.jenis_kayu as jenis_kayu_vakum_line,
                                b.kode as kode_vakum_line,
                                b.diameter1 as diameter1_vakum_line,
                                b.diameter2 as diameter2_vakum_line,
                                b.panjang as panjang_vakum_line,
                                b.log_pakai_pcs as log_pakai_pcs_vakum_line,
                                b.log_pakai_m3 as log_pakai_m3_vakum_line,
                                a.id as id_vakum_detail,
                                a.name as name_vakum_detail,
                                a.tebal as tebal_vakum_detail,
                                a.lebar as lebar_vakum_detail,
                                a.panjang as panjang_vakum_detail,
                                a.hasil_keping as hasil_keping_vakum_detail,
                                a.hasil_m3 as hasil_m3_vakum_detail,
                                a.shift as shift_vakum_detail,
                                a.grade as grade_vakum_detail,
                                a.fsc as fas_vakum_detail,
                                a.vakum_celup as vakum_celup_detail
                            from kb_mrp_vakum_celup_line_detail a
                            join kb_mrp_vakum_celup_line b on b.id = a.kb_mrp_vakum_celup_line_id 
                            join kb_mrp_vakum_celup c on c.id = b.kb_mrp_vakum_celup_id 
                            where c.id in {_vakum_celup}
                            order by c.id, b.id, a.id asc)""".format(_vakum_celup=tuple(active_ids)))
        dict_vakum_celup = self._cr.dictfetchall()
        if len(dict_vakum_celup) > 0:
            ins_values = ",".join([u"({},'{}','{}','{}',{},'{}','{}','{}',{},{},{},{},{},{},'{}',{},{},{},{},{},'{}',{},{},'{}','{}','{}')".format(
                data['id_vakum'] or 'Null',
                data['name_vakum'] or '',
                data['tanggal_selesai_vakum'] or 'Null',
                data['keterangan_vakum'] or '',
                data['id_vakum_line'] or 'Null',
                data['name_vakum_line'] or '',
                data['jenis_kayu_vakum_line'] or '',
                data['kode_vakum_line'] or '',
                data['diameter1_vakum_line'] or 0,
                data['diameter2_vakum_line'] or 0,
                data['panjang_vakum_line'] or 0,
                data['log_pakai_pcs_vakum_line'] or 0,
                data['log_pakai_m3_vakum_line'] or 0,
                data['id_vakum_detail'] or 'Null',
                data['name_vakum_detail'] or '',
                data['tebal_vakum_detail'] or 0,
                data['lebar_vakum_detail'] or 0,
                data['panjang_vakum_detail'] or 0,
                data['hasil_keping_vakum_detail'] or 0,
                data['hasil_m3_vakum_detail'] or 0,
                data['shift_vakum_detail'] or '',
                self._uid,
                new_report_vakum_celup.id,
                data['grade_vakum_detail'] or '',
                data['fas_vakum_detail'] or '',
                data['vakum_celup_detail'] or ''
            ) for data in dict_vakum_celup])
            insert_query = u"insert into kb_mrp_vakum_celup_report_line (kb_mrp_vakum_celup_id,name_header,tanggal_selesai_vakum,keterangan," \
                           u"kb_mrp_vakum_celup_line_id,name_line,jenis_kayu,kode,diameter1,diameter2,panjang_line,log_pakai_pcs," \
                           u"log_pakai_m3,kb_mrp_vakum_celup_line_detail_id,name_detail,tebal,lebar,panjang_detail,hasil_keping," \
                           u"hasil_m3,shift,create_uid,vakum_celup_report_id,grade,fsc,vakum_celup) values {_values}".format(_values=ins_values)
            self._cr.execute(insert_query)
            self._cr.commit()
            return {
                'type': 'ir.actions.act_url',
                'url': '/kb_mrp_vakum_celup_report/%s' % (new_report_vakum_celup.id),
                'target': 'new',
            }



    @api.model
    def create(self, vals):
        res = super(kb_mrp_vakum_celup, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.vakum.celup') or '/'
                rec.name = seq
        return res

    @api.onchange('no_nota')
    def func_onchange_no_nota(self):
        # logic baru
        trigger_id = 0
        if self.no_nota.id == False:
            if self.kb_mrp_vakum_celup_ids:
                check_detail = self.env['kb.mrp.vakum.celup.line.detail'].search([('kb_mrp_vakum_celup_line_id','in',self.kb_mrp_vakum_celup_ids.ids)])
                if check_detail:
                    check_detail.unlink()
                self.kb_mrp_vakum_celup_ids.unlink()
            self.no_nota = None
        else:
            trigger_id = self.no_nota.id
            if len(self.kb_mrp_vakum_celup_ids.ids) > 0:
                if self.kb_mrp_vakum_celup_ids:
                    list_check_line = self.kb_mrp_vakum_celup_ids.ids
                    list_check_line.append(0)
                    list_check_line.append(0)
                    check_detail = self.env['kb.mrp.vakum.celup.line.detail'].search([('kb_mrp_vakum_celup_line_id', 'in', self.kb_mrp_vakum_celup_ids.ids)])
                    if check_detail:
                        list_check_detail = check_detail.ids
                        list_check_detail.append(0)
                        list_check_detail.append(0)
                        check_detail.unlink()
                    self.kb_mrp_vakum_celup_ids.unlink()
            if len(self.kb_mrp_vakum_celup_ids.ids) == 0:
                check_nota = self.env['kb.mrp.sawmil'].search([('id', '=', trigger_id)])
                if check_nota:
                    for line in check_nota.kb_mrp_sawmil_ids:
                        vals_detail = []
                        for d in line.kb_mrp_sawmil_line_ids:
                            vals_detail.append((0,0,{
                                'tebal' : d.tebal,
                                'lebar' : d.lebar,
                                'panjang' : d.panjang,
                                'hasil_keping': d.hasil_keping,
                                'hasil_m3': d.hasil_m3,
                                'shift': d.shift,
                                'kb_mrp_sawmil_line_detail_id': d.id
                            }))
                        vals_line = {
                            'jenis_kayu' : line.jenis_kayu,
                            'kb_mrp_vakum_celup_id' : self.id,
                            'kode' : line.kode,
                            'diameter1' : line.diameter1,
                            'diameter2' : line.diameter2,
                            'panjang' : line.panjang,
                            'log_pakai_pcs' : line.log_pakai_pcs,
                            'log_pakai_m3' : line.log_pakai_m3,
                            'kb_mrp_sawmil_line_id' : line.id,
                            'kb_mrp_vakum_celup_line_ids' : vals_detail
                        }
                        new_celup = self.env['kb.mrp.vakum.celup.line'].create(vals_line)
                    self.no_nota = check_nota.id


    name = fields.Char(string="No Vakum", default="New")
    tahun = fields.Char(string="Tahun")
    tanggal_selesai_vakum = fields.Date(string="Tanggal Selesai Vakum")
    no_nota = fields.Many2one("kb.mrp.sawmil")
    keterangan = fields.Text(string="Keterangan")
    kb_mrp_vakum_celup_ids = fields.One2many('kb.mrp.vakum.celup.line', 'kb_mrp_vakum_celup_id', string="Kb Mrp Vakum Celup Ids")

class kb_mrp_vakum_celup_line(models.Model):
    _name = 'kb.mrp.vakum.celup.line'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_vakum_celup_line, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.vakum.celup.line') or '/'
                rec.name = seq
        return res

    def func_vakum_celup_line_detail(self):
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id('kb_mrp_production.kb_mrp_vakum_celup_line_id')
        return {
            'name': 'Detail',
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'kb.mrp.vakum.celup.line',
            'views': [[form_view_id, 'form']],
            'target': 'new',
            'res_id': self.id,
        }

    def func_ok(self):
        pass

    name = fields.Char(string="No Vakum Line", default="New")
    kb_mrp_vakum_celup_id = fields.Many2one('kb.mrp.vakum.celup', string="No Vakum")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    item = fields.Char(string="Item")
    kode = fields.Char(string="Kode")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang = fields.Float(string="Panjang")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    no_chamber = fields.Float(striing="No Chamber")
    kb_mrp_vakum_celup_line_ids = fields.One2many('kb.mrp.vakum.celup.line.detail', 'kb_mrp_vakum_celup_line_id', string="Kb Mrp Vakum Celup Line Detail Ids")
    kb_mrp_sawmil_line_id = fields.Many2one('kb.mrp.sawmil.line')

class kb_mrp_vakum_celup_line_detail(models.Model):
    _name = 'kb.mrp.vakum.celup.line.detail'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_vakum_celup_line_detail, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.vakum.celup.line.detail') or '/'
                rec.name = seq
        return res

    name = fields.Char(string="No Detail Vakum", default="New")
    kb_mrp_vakum_celup_line_id = fields.Many2one('kb.mrp.vakum.celup.line', string="Kb Mrp Vakum Celup Line Id")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang = fields.Float(string="Panjang")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    vakum_celup = fields.Selection([('vakum', 'Vakum'), ('celup', 'Celup'),('vakum_&_celup', 'Vakum & Celup'),('tidak_sama_sekali','Tidak Sama Sekali')])
    kb_mrp_sawmil_line_detail_id = fields.Many2one('kb.mrp.sawmil.line.detail')

class kb_mrp_sticking(models.Model):
    _name = 'kb.mrp.sticking'

    def funct_print_excel_sticking(self):
        context = self._context.copy()
        active_ids = context.get('active_ids', [])
        active_ids.append(0)
        active_ids.append(0)
        new_report_sticking = self.env['kb.mrp.sticking.report'].sudo().create({'name': 'New'})
        self._cr.execute("""(select
                                   c.id as id_sticking,
                                   c.name as name_sticking,
                                   c.tanggal_selesai_vakum as tanggal_selesai_vakum,
                                   c.tanggal_selesai_stick as tanggal_selesai_stick,
                                   c.keterangan as keterangan_sticking,
                                   b.id as id_sticking_line,
                                   b.name as name_sticking_line,
                                   b.jenis_kayu as jenis_kayu_sticking_line,
                                   b.kode as kode_sticking_line,
                                   b.diameter1 as diameter1_sticking_line,
                                   b.diameter2 as diameter2_sticking_line,
                                   b.panjang as panjang_sticking_line,
                                   b.log_pakai_pcs as log_pakai_pcs_sticking_line,
                                   b.log_pakai_m3 as log_pakai_m3_sticking_line,
                                   a.id as id_sticking_detail,
                                   a.name as name_sticking_detail,
                                   a.tebal as tebal_sticking_detail,
                                   a.lebar as lebar_sticking_detail,
                                   a.panjang as panjang_sticking_detail,
                                   a.hasil_keping as hasil_keping_sticking_detail,
                                   a.hasil_m3 as hasil_m3_sticking_detail,
                                   a.shift as shift_sticking_detail,
                                   a.grade as grade_sticking_detail,
                                   a.fsc as fas_sticking_detail
                               from kb_mrp_sticking_line_detail a
                               join kb_mrp_sticking_line b on b.id = a.kb_mrp_sticking_line_id
                               join kb_mrp_sticking c on c.id = b.kb_mrp_sticking_id 
                               where c.id in {_sticking}
                               order by c.id, b.id, a.id asc)""".format(_sticking=tuple(active_ids)))
        dict_sticking = self._cr.dictfetchall()
        if len(dict_sticking) > 0:
            ins_values = ",".join([
                u"({},'{}','{}','{}','{}',{},'{}','{}','{}',{},{},{},{},{},{},'{}',{},{},{},{},{},'{}',{},{},'{}','{}')".format(
                    data['id_sticking'] or 'Null',
                    data['name_sticking'] or '',
                    data['tanggal_selesai_vakum'] or 'Null',
                    data['tanggal_selesai_stick'] or 'Null',
                    data['keterangan_sticking'] or '',
                    data['id_sticking_line'] or 'Null',
                    data['name_sticking_line'] or '',
                    data['jenis_kayu_sticking_line'] or '',
                    data['kode_sticking_line'] or '',
                    data['diameter1_sticking_line'] or 0,
                    data['diameter2_sticking_line'] or 0,
                    data['panjang_sticking_line'] or 0,
                    data['log_pakai_pcs_sticking_line'] or 0,
                    data['log_pakai_m3_sticking_line'] or 0,
                    data['id_sticking_detail'] or 'Null',
                    data['name_sticking_detail'] or '',
                    data['tebal_sticking_detail'] or 0,
                    data['lebar_sticking_detail'] or 0,
                    data['panjang_sticking_detail'] or 0,
                    data['hasil_keping_sticking_detail'] or 0,
                    data['hasil_m3_sticking_detail'] or 0,
                    data['shift_sticking_detail'] or '',
                    self._uid,
                    new_report_sticking.id,
                    data['grade_sticking_detail'] or '',
                    data['fas_sticking_detail'] or ''
                ) for data in dict_sticking])
            insert_query = u"insert into kb_mrp_sticking_report_line (kb_mrp_sticking_id,name_header,tanggal_selesai_vakum,tanggal_selesai_stick,keterangan," \
                           u"kb_mrp_sticking_line_id,name_line,jenis_kayu,kode,diameter1,diameter2,panjang_line,log_pakai_pcs," \
                           u"log_pakai_m3,kb_mrp_sticking_line_detail_id,name_detail,tebal,lebar,panjang_detail,hasil_keping," \
                           u"hasil_m3,shift,create_uid,sticking_report_id,grade,fsc) values {_values}".format(
                _values=ins_values)
            self._cr.execute(insert_query)
            self._cr.commit()
            return {
                'type': 'ir.actions.act_url',
                'url': '/kb_mrp_sticking_report/%s' % (new_report_sticking.id),
                'target': 'new',
            }

    @api.model
    def create(self, vals):
        res = super(kb_mrp_sticking, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.sticking') or '/'
                rec.name = seq
            rec.tanggal_selesai_vakum = rec.tanggal_helper_vakum
        return res

    def write(self, vals):
        res = super(kb_mrp_sticking, self).write(vals)
        if 'tanggal_helper_vakum' in vals:
            self.tanggal_selesai_vakum = vals['tanggal_helper_vakum']
        return res

    @api.onchange('no_vakum_celup')
    def func_onchange_no_vakum_celup(self):
        # logic baru
        trigger_id = 0
        if self.no_vakum_celup.id == False:
            if self.kb_mrp_sticking_ids:
                check_detail = self.env['kb.mrp.sticking.line.detail'].search([('kb_mrp_sticking_line_id','in',self.kb_mrp_sticking_ids.ids)])
                if check_detail:
                    check_detail.unlink()
                self.kb_mrp_sticking_ids.unlink()
            self.no_vakum_celup = None
            self.tanggal_selesai_vakum = False
            self.tanggal_helper_vakum = False
        else:
            trigger_id = self.no_vakum_celup.id
            if len(self.kb_mrp_sticking_ids.ids) > 0:
                if self.kb_mrp_sticking_ids:
                    list_check_line = self.kb_mrp_sticking_ids.ids
                    list_check_line.append(0)
                    list_check_line.append(0)
                    check_detail = self.env['kb.mrp.sticking.line.detail'].search([('kb_mrp_sticking_line_id', 'in', self.kb_mrp_sticking_ids.ids)])
                    if check_detail:
                        list_check_detail = check_detail.ids
                        list_check_detail.append(0)
                        list_check_detail.append(0)
                        check_detail.unlink()
                    self.kb_mrp_sticking_ids.unlink()
            if len(self.kb_mrp_sticking_ids.ids) == 0:
                check_vakum_celup = self.env['kb.mrp.vakum.celup'].search([('id', '=', trigger_id)])
                if check_vakum_celup:
                    for line in check_vakum_celup.kb_mrp_vakum_celup_ids:
                        vals_detail=[]
                        for d in line.kb_mrp_vakum_celup_line_ids:
                            vals_detail.append((0,0,{
                                'tebal': d.tebal,
                                'lebar': d.lebar,
                                'panjang': d.panjang,
                                'hasil_keping': d.hasil_keping,
                                'hasil_m3': d.hasil_m3,
                                'shift': d.shift,
                                'grade': d.grade,
                                'fsc': d.fsc,
                                'vakum_celup': d.vakum_celup,
                                'kb_mrp_vakum_celup_line_detail_id': d.id,
                            }))
                        vals_line = {
                            'jenis_kayu': line.jenis_kayu,
                            'kb_mrp_sticking_id' : self.id,
                            'item': line.item,
                            'kode': line.kode,
                            'diameter1': line.diameter1,
                            'diameter2': line.diameter2,
                            'panjang': line.panjang,
                            'log_pakai_pcs': line.log_pakai_pcs,
                            'log_pakai_m3': line.log_pakai_m3,
                            'no_chamber': line.no_chamber,
                            'kb_mrp_vakum_celup_line_id': line.id,
                            'kb_mrp_sticking_line_ids': vals_detail,
                        }
                        new_sticking = self.env['kb.mrp.sticking.line'].create(vals_line)
                    self.no_vakum_celup = check_vakum_celup.id
                self.tanggal_selesai_vakum = self.no_vakum_celup.tanggal_selesai_vakum
                self.tanggal_helper_vakum = self.no_vakum_celup.tanggal_selesai_vakum

    name = fields.Char(string="No Sticking", default="New")
    tahun = fields.Char(string="Tahun")
    tanggal_selesai_vakum = fields.Date(string="Tanggal Selesai Vakum")
    tanggal_selesai_stick = fields.Date(string="Tanggal Selesai Stick")
    tanggal_helper_vakum = fields.Date(string="Tanggal Helper Vakum")
    no_vakum_celup = fields.Many2one("kb.mrp.vakum.celup")
    keterangan = fields.Text(string="Keterangan")
    kb_mrp_sticking_ids = fields.One2many('kb.mrp.sticking.line', 'kb_mrp_sticking_id', string="Kb Mrp Sticking Ids")

class kb_mrp_sticking_line(models.Model):
    _name = 'kb.mrp.sticking.line'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_sticking_line, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.sticking.line') or '/'
                rec.name = seq
        return res

    def func_sticking_line_detail(self):
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id('kb_mrp_production.kb_mrp_sticking_line_id')
        return {
            'name': 'Detail',
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'kb.mrp.sticking.line',
            'views': [[form_view_id, 'form']],
            'target': 'new',
            'res_id': self.id,
        }

    def func_ok(self):
        pass

    name = fields.Char(string="No Sticking Line", default="New")
    kb_mrp_sticking_id = fields.Many2one('kb.mrp.sticking', string="No Sticking")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    item = fields.Char(string="Item")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang = fields.Float(string="Panjang")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    no_chamber = fields.Char(string="No Chamber")
    kb_mrp_sticking_line_ids = fields.One2many('kb.mrp.sticking.line.detail', 'kb_mrp_sticking_line_id', string="Kb Mrp Sticking Line Detail Ids")
    kb_mrp_vakum_celup_line_id = fields.Many2one('kb.mrp.vakum.celup.line')

class kb_mrp_sticking_line_detail(models.Model):
    _name = 'kb.mrp.sticking.line.detail'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_sticking_line_detail, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.sticking.line.detail') or '/'
                rec.name = seq
        return res

    name = fields.Char(string="No Detail Sticking", default="New")
    kb_mrp_sticking_line_id = fields.Many2one('kb.mrp.sticking.line', string="Kb Mrp Sticking Line Id")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang = fields.Float(string="Panjang")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    vakum_celup = fields.Char(string="Vakum / Celup")
    kb_mrp_vakum_celup_line_detail_id = fields.Many2one('kb.mrp.vakum.celup.line.detail')

class kb_mrp_oven(models.Model):
    _name = 'kb.mrp.oven'

    def funct_print_excel_oven(self):
        context = self._context.copy()
        active_ids = context.get('active_ids', [])
        active_ids.append(0)
        active_ids.append(0)
        new_report_oven = self.env['kb.mrp.oven.report'].sudo().create({'name': 'New'})
        self._cr.execute("""(select
                                   c.id as id_oven,
                                   c.name as name_oven,
                                   c.tanggal_masuk_oven as tanggal_masuk_oven,
                                   c.tanggal_selesai_vakum as tanggal_selesai_vakum,
                                   c.tanggal_selesai_stick as tanggal_selesai_stick,
                                   c.tanggal_keluar_oven as tanggal_keluar_oven,
                                   c.keterangan as keterangan_oven,
                                   b.id as id_oven_line,
                                   b.name as name_oven_line,
                                   b.jenis_kayu as jenis_kayu_oven_line,
                                   b.kode as kode_oven_line,
                                   b.diameter1 as diameter1_oven_line,
                                   b.diameter2 as diameter2_oven_line,
                                   b.panjang as panjang_oven_line,
                                   b.log_pakai_pcs as log_pakai_pcs_oven_line,
                                   b.log_pakai_m3 as log_pakai_m3_oven_line,
                                   a.id as id_oven_detail,
                                   a.name as name_oven_detail,
                                   a.tebal as tebal_oven_detail,
                                   a.lebar as lebar_oven_detail,
                                   a.panjang as panjang_oven_detail,
                                   a.hasil_keping as hasil_keping_oven_detail,
                                   a.hasil_m3 as hasil_m3_oven_detail,
                                   a.shift as shift_oven_detail,
                                   a.grade as grade_oven_detail,
                                   a.fsc as fas_oven_detail,
                                   a.vakum_celup as vakum_celup_detail
                               from kb_mrp_oven_line_detail a
                               join kb_mrp_oven_line b on b.id = a.kb_mrp_oven_line_id
                               join kb_mrp_oven c on c.id = b.kb_mrp_oven_id 
                               where c.id in {_oven}
                               order by c.id, b.id, a.id asc)""".format(_oven=tuple(active_ids)))
        dict_oven = self._cr.dictfetchall()
        if len(dict_oven) > 0:
            ins_values = ",".join([
                u"({},'{}','{}','{}','{}','{}','{}',{},'{}','{}','{}',{},{},{},{},{},{},'{}',{},{},{},{},{},'{}',{},{},'{}','{}','{}')".format(
                    data['id_oven'] or 'Null',
                    data['name_oven'] or '',
                    data['tanggal_masuk_oven'] or 'Null',
                    data['tanggal_selesai_vakum'] or 'Null',
                    data['tanggal_selesai_stick'] or 'Null',
                    data['tanggal_keluar_oven'] or 'Null',
                    data['keterangan_oven'] or '',
                    data['id_oven_line'] or 'Null',
                    data['name_oven_line'] or '',
                    data['jenis_kayu_oven_line'] or '',
                    data['kode_oven_line'] or '',
                    data['diameter1_oven_line'] or 0,
                    data['diameter2_oven_line'] or 0,
                    data['panjang_oven_line'] or 0,
                    data['log_pakai_pcs_oven_line'] or 0,
                    data['log_pakai_m3_oven_line'] or 0,
                    data['id_oven_detail'] or 'Null',
                    data['name_oven_detail'] or '',
                    data['tebal_oven_detail'] or 0,
                    data['lebar_oven_detail'] or 0,
                    data['panjang_oven_detail'] or 0,
                    data['hasil_keping_oven_detail'] or 0,
                    data['hasil_m3_oven_detail'] or 0,
                    data['shift_oven_detail'] or '',
                    self._uid,
                    new_report_oven.id,
                    data['grade_oven_detail'] or '',
                    data['fas_oven_detail'] or '',
                    data['vakum_celup_detail'] or ''
                ) for data in dict_oven])
            insert_query = u"insert into kb_mrp_oven_report_line (kb_mrp_oven_id,name_header,tanggal_masuk_oven,tanggal_selesai_vakum,tanggal_selesai_stick,tanggal_keluar_oven,keterangan," \
                           u"kb_mrp_oven_line_id,name_line,jenis_kayu,kode,diameter1,diameter2,panjang_line,log_pakai_pcs," \
                           u"log_pakai_m3,kb_mrp_oven_line_detail_id,name_detail,tebal,lebar,panjang_detail,hasil_keping," \
                           u"hasil_m3,shift,create_uid,oven_report_id,grade,fsc,vakum_celup) values {_values}".format(
                _values=ins_values)
            self._cr.execute(insert_query)
            self._cr.commit()
            return {
                'type': 'ir.actions.act_url',
                'url': '/kb_mrp_oven_report/%s' % (new_report_oven.id),
                'target': 'new',
            }

    @api.model
    def create(self, vals):
        res = super(kb_mrp_oven, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.oven') or '/'
                rec.name = seq
            rec.tanggal_selesai_vakum = rec.tanggal_helper_vakum
            rec.tanggal_selesai_stick = rec.tanggal_helper_stick
        return res

    def write(self, vals):
        res = super(kb_mrp_oven, self).write(vals)
        if 'tanggal_helper_vakum' in vals:
            self.tanggal_selesai_vakum = vals['tanggal_helper_vakum']
            self.tanggal_selesai_stick = vals['tanggal_helper_stick']
        return res

    @api.onchange('no_sticking')
    def func_onchange_no_sticking(self):
        # logic baru
        trigger_id = 0
        if self.no_sticking.id == False:
            if self.kb_mrp_oven_ids:
                check_detail = self.env['kb.mrp.oven.line.detail'].search([('kb_mrp_oven_line_id','in',self.kb_mrp_oven_ids.ids)])
                if check_detail:
                    check_detail.unlink()
                self.kb_mrp_oven_ids.unlink()
            self.no_sticking = None
            self.tanggal_selesai_vakum = False
            self.tanggal_helper_vakum = False
            self.tanggal_selesai_stick = False
            self.tanggal_helper_stick = False
        else:
            trigger_id = self.no_sticking.id
            if len(self.kb_mrp_oven_ids.ids) > 0:
                if self.kb_mrp_oven_ids:
                    list_check_line = self.kb_mrp_oven_ids.ids
                    list_check_line.append(0)
                    list_check_line.append(0)
                    check_detail = self.env['kb.mrp.oven.line.detail'].search([('kb_mrp_oven_line_id', 'in', self.kb_mrp_oven_ids.ids)])
                    if check_detail:
                        list_check_detail = check_detail.ids
                        list_check_detail.append(0)
                        list_check_detail.append(0)
                        check_detail.unlink()
                    self.kb_mrp_oven_ids.unlink()
            if len(self.kb_mrp_oven_ids.ids) == 0:
                check_sticking = self.env['kb.mrp.sticking'].search([('id', '=', trigger_id)])
                if check_sticking:
                    for line in check_sticking.kb_mrp_sticking_ids:
                        vals_detail=[]
                        for d in line.kb_mrp_sticking_line_ids:
                            vals_detail.append((0,0,{
                                'tebal': d.tebal,
                                'lebar': d.lebar,
                                'panjang': d.panjang,
                                'hasil_keping': d.hasil_keping,
                                'hasil_m3': d.hasil_m3,
                                'shift': d.shift,
                                'grade': d.grade,
                                'fsc': d.fsc,
                                'vakum_celup': d.vakum_celup,
                                'kb_mrp_sticking_line_detail_id': d.id,
                            }))
                        vals_line = {
                            'jenis_kayu': line.jenis_kayu,
                            'kb_mrp_oven_id' : self.id,
                            'item': line.item,
                            'kode': line.kode,
                            'diameter1': line.diameter1,
                            'diameter2': line.diameter2,
                            'panjang': line.panjang,
                            'log_pakai_pcs': line.log_pakai_pcs,
                            'log_pakai_m3': line.log_pakai_m3,
                            'no_chamber': line.no_chamber,
                            'kb_mrp_sticking_line_id': line.id,
                            'kb_mrp_oven_line_ids': vals_detail,
                        }
                        new_sticking = self.env['kb.mrp.oven.line'].create(vals_line)
                    self.no_sticking = check_sticking.id
                    self.tanggal_selesai_vakum = self.no_sticking.tanggal_selesai_vakum
                    self.tanggal_helper_vakum = self.no_sticking.tanggal_selesai_vakum
                    self.tanggal_selesai_stick = self.no_sticking.tanggal_selesai_stick
                    self.tanggal_helper_stick = self.no_sticking.tanggal_selesai_stick

    name = fields.Char(string="No Oven", default="New")
    tahun = fields.Char(string="Tahun")
    tanggal_selesai_vakum = fields.Date(string="Tanggal Selesai Vakum")
    tanggal_helper_vakum = fields.Date(string="Tanggal Helper Vakum")
    tanggal_selesai_stick = fields.Date(string="Tanggal Selesai Stick")
    tanggal_helper_stick = fields.Date(string="Tanggal Helper Stick")
    tanggal_masuk_oven = fields.Date(string="Tanggal Masuk Oven")
    tanggal_keluar_oven = fields.Date(string="Tanggal Keluar Oven")
    no_sticking = fields.Many2one("kb.mrp.sticking")
    keterangan = fields.Text(string="Keterangan")
    kb_mrp_oven_ids = fields.One2many('kb.mrp.oven.line', 'kb_mrp_oven_id', string="Kb Mrp Oven Ids")

class kb_mrp_oven_line(models.Model):
    _name = 'kb.mrp.oven.line'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_oven_line, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.oven.line') or '/'
                rec.name = seq
        return res

    def func_oven_line_detail(self):
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id('kb_mrp_production.kb_mrp_oven_line_id')
        return {
            'name': 'Detail',
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'kb.mrp.oven.line',
            'views': [[form_view_id, 'form']],
            'target': 'new',
            'res_id': self.id,
        }

    def func_ok(self):
        pass

    name = fields.Char(string="No Oven Line", default="New")
    kb_mrp_oven_id = fields.Many2one('kb.mrp.oven', string="No Oven")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    item = fields.Char(string="Item")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang = fields.Float(string="Panjang")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    no_chamber = fields.Char(string="No Chamber")
    kb_mrp_oven_line_ids = fields.One2many('kb.mrp.oven.line.detail', 'kb_mrp_oven_line_id', string="Kb Mrp Oven Line Detail Ids")
    kb_mrp_sticking_line_id = fields.Many2one('kb.mrp.sticking.line')

class kb_mrp_oven_line_detail(models.Model):
    _name = 'kb.mrp.oven.line.detail'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_oven_line_detail, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.oven.line.detail') or '/'
                rec.name = seq
        return res

    name = fields.Char(string="No Detail Oven", default="New")
    kb_mrp_oven_line_id = fields.Many2one('kb.mrp.oven.line', string="Kb Mrp Oven Line Id")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang = fields.Float(string="Panjang")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    vakum_celup = fields.Char(string="Vakum / Celup")
    kb_mrp_sticking_line_detail_id = fields.Many2one('kb.mrp.sticking.line.detail')

class kb_mrp_gudang_kering(models.Model):
    _name = 'kb.mrp.gudang.kering'

    def funct_print_excel_gudang_kering(self):
        context = self._context.copy()
        active_ids = context.get('active_ids', [])
        active_ids.append(0)
        active_ids.append(0)
        new_report_gudang_kering = self.env['kb.mrp.gudang.kering.report'].sudo().create({'name': 'New'})
        self._cr.execute("""(select
                                   c.id as id_gudang_kering,
                                   c.name as name_gudang_kering,
                                   c.tanggal_selesai_stick as tanggal_selesai_stick,
                                   c.tanggal_masuk_oven as tanggal_masuk_oven,
                                   c.tanggal_keluar_oven as tanggal_keluar_oven,
                                   c.tanggal_in as tanggal_in_gd,
                                   c.tanggal_out as tanggal_out_gd,
                                   c.keterangan as keterangan_gudang_kering,
                                   b.id as id_gudang_kering_line,
                                   b.name as name_gudang_kering_line,
                                   b.jenis_kayu as jenis_kayu_gudang_kering_line,
                                   b.kode as kode_gudang_kering_line,
                                   b.diameter1 as diameter1_gudang_kering_line,
                                   b.diameter2 as diameter2_gudang_kering_line,
                                   b.panjang as panjang_gudang_kering_line,
                                   b.log_pakai_pcs as log_pakai_pcs_gudang_kering_line,
                                   b.log_pakai_m3 as log_pakai_m3_gudang_kering_line,
                                   b.no_chamber as no_chamber_gudang_kering_line,
                                   a.id as id_gudang_kering_detail,
                                   a.name as name_gudang_kering_detail,
                                   a.tebal as tebal_gudang_kering_detail,
                                   a.lebar as lebar_gudang_kering_detail,
                                   a.panjang as panjang_gudang_kering_detail,
                                   a.hasil_keping as hasil_keping_gudang_kering_detail,
                                   a.hasil_m3 as hasil_m3_gudang_kering_detail,
                                   a.shift as shift_gudang_kering_detail,
                                   a.grade as grade_gudang_kering_detail,
                                   a.fsc as fsc_gudang_kering_detail,
                                   a.vakum_celup as vakum_celup_gudang_kering_detail
                               from kb_mrp_gudang_kering_line_detail a
                               join kb_mrp_gudang_kering_line b on b.id = a.kb_mrp_gudang_kering_line_id
                               join kb_mrp_gudang_kering c on c.id = b.kb_mrp_gudang_kering_id 
                               where c.id in {_gudang_kering}
                               order by c.id, b.id, a.id asc)""".format(_gudang_kering=tuple(active_ids)))
        dict_sticking = self._cr.dictfetchall()
        if len(dict_sticking) > 0:
            ins_values = ",".join([
                u"({},'{}','{}','{}','{}','{}','{}','{}',{},'{}','{}','{}',{},{},{},{},{},{},'{}',{},{},{},{},{},'{}',{},{},'{}','{}',{},'{}')".format(
                    data['id_gudang_kering'] or 'Null',
                    data['name_gudang_kering'] or '',
                    data['tanggal_selesai_stick'] or 'Null',
                    data['tanggal_masuk_oven'] or 'Null',
                    data['tanggal_keluar_oven'] or 'Null',
                    data['tanggal_in_gd'] or 'Null',
                    data['tanggal_out_gd'] or 'Null',
                    data['keterangan_gudang_kering'] or '',
                    data['id_gudang_kering_line'] or 'Null',
                    data['name_gudang_kering_line'] or '',
                    data['jenis_kayu_gudang_kering_line'] or '',
                    data['kode_gudang_kering_line'] or '',
                    data['diameter1_gudang_kering_line'] or 0,
                    data['diameter2_gudang_kering_line'] or 0,
                    data['panjang_gudang_kering_line'] or 0,
                    data['log_pakai_pcs_gudang_kering_line'] or 0,
                    data['log_pakai_m3_gudang_kering_line'] or 0,
                    data['id_gudang_kering_detail'] or 'Null',
                    data['name_gudang_kering_detail'] or '',
                    data['tebal_gudang_kering_detail'] or 0,
                    data['lebar_gudang_kering_detail'] or 0,
                    data['panjang_gudang_kering_detail'] or 0,
                    data['hasil_keping_gudang_kering_detail'] or 0,
                    data['hasil_m3_gudang_kering_detail'] or 0,
                    data['shift_gudang_kering_detail'] or '',
                    self._uid,
                    new_report_gudang_kering.id,
                    data['grade_gudang_kering_detail'] or '',
                    data['fsc_gudang_kering_detail'] or '',
                    data['no_chamber_gudang_kering_line'] or 0,
                    data['vakum_celup_gudang_kering_detail'] or '',
                ) for data in dict_sticking])
            insert_query = u"insert into kb_mrp_gudang_kering_report_line (kb_mrp_gudang_kering_id,name_header,tanggal_selesai_stick,tanggal_masuk_oven," \
                           u"tanggal_keluar_oven,tanggal_in_gd,tanggal_out_gd,keterangan," \
                           u"kb_mrp_gudang_kering_line_id,name_line,jenis_kayu,kode,diameter1,diameter2,panjang_line,log_pakai_pcs," \
                           u"log_pakai_m3,kb_mrp_gudang_kering_line_detail_id,name_detail,tebal,lebar,panjang_detail,hasil_keping," \
                           u"hasil_m3,shift,create_uid,gudang_kering_report_id,grade,fsc,no_chamber,vakum_celup) values {_values}".format(
                _values=ins_values)
            self._cr.execute(insert_query)
            self._cr.commit()
            return {
                'type': 'ir.actions.act_url',
                'url': '/kb_mrp_gudang_kering_report/%s' % (new_report_gudang_kering.id),
                'target': 'new',
            }


    @api.model
    def create(self, vals):
        res = super(kb_mrp_gudang_kering, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.gudang.kering') or '/'
                rec.name = seq
            rec.tanggal_selesai_stick = rec.tanggal_helper_stick
            rec.tanggal_masuk_oven = rec.tanggal_helper_masukoven
            rec.tanggal_keluar_oven = rec.tanggal_helper_keluaroven
        return res

    def write(self, vals):
        res = super(kb_mrp_gudang_kering, self).write(vals)
        if 'tanggal_helper_stick' in vals:
            self.tanggal_selesai_stick = vals['tanggal_helper_stick']
            self.tanggal_masuk_oven = vals['tanggal_helper_masukoven']
            self.tanggal_keluar_oven = vals['tanggal_helper_keluaroven']
        return res

    @api.onchange('no_oven')
    def func_onchange_no_oven(self):
        # logic baru
        trigger_id = 0
        if self.no_oven.id == False:
            if self.kb_mrp_gudang_kering_ids:
                check_detail = self.env['kb.mrp.gudang.kering.line.detail'].search([('kb_mrp_gudang_kering_line_id','in',self.kb_mrp_gudang_kering_ids.ids)])
                if check_detail:
                    check_detail.unlink()
                self.kb_mrp_gudang_kering_ids.unlink()
            self.no_oven = None
            self.tanggal_keluar_oven = False
            self.tanggal_helper_keluaroven = False
            self.tanggal_masuk_oven = False
            self.tanggal_helper_masukoven = False
            self.tanggal_selesai_stick = False
            self.tanggal_helper_stick = False
        else:
            trigger_id = self.no_oven.id
            if len(self.kb_mrp_gudang_kering_ids.ids) > 0:
                if self.kb_mrp_gudang_kering_ids:
                    list_check_line = self.kb_mrp_gudang_kering_ids.ids
                    list_check_line.append(0)
                    list_check_line.append(0)
                    check_detail = self.env['kb.mrp.gudang.kering.line.detail'].search([('kb_mrp_gudang_kering_line_id', 'in', self.kb_mrp_gudang_kering_ids.ids)])
                    if check_detail:
                        list_check_detail = check_detail.ids
                        list_check_detail.append(0)
                        list_check_detail.append(0)
                        check_detail.unlink()
                    self.kb_mrp_gudang_kering_ids.unlink()
            if len(self.kb_mrp_gudang_kering_ids.ids) == 0:
                check_oven = self.env['kb.mrp.oven'].search([('id', '=', trigger_id)])
                if check_oven:
                    for line in check_oven.kb_mrp_oven_ids:
                        vals_detail=[]
                        for d in line.kb_mrp_oven_line_ids:
                            vals_detail.append((0,0,{
                                'tebal': d.tebal,
                                'lebar': d.lebar,
                                'panjang': d.panjang,
                                'hasil_keping': d.hasil_keping,
                                'hasil_m3': d.hasil_m3,
                                'shift': d.shift,
                                'vakum_celup': d.vakum_celup,
                                'grade': d.grade,
                                'fsc': d.fsc,
                                'kb_mrp_oven_line_detail_id': d.id,
                            }))
                        vals_line = {
                            'jenis_kayu': line.jenis_kayu,
                            'kb_mrp_gudang_kering_id' : self.id,
                            'item': line.item,
                            'kode': line.kode,
                            'diameter1': line.diameter1,
                            'diameter2': line.diameter2,
                            'panjang': line.panjang,
                            'log_pakai_pcs': line.log_pakai_pcs,
                            'log_pakai_m3': line.log_pakai_m3,
                            'no_chamber': line.no_chamber,
                            'kb_mrp_oven_line_id': line.id,
                            'kb_mrp_gudang_kering_line_ids': vals_detail,
                        }
                        new_oven = self.env['kb.mrp.gudang.kering.line'].create(vals_line)
                    self.no_oven = check_oven.id
                    self.tanggal_selesai_stick = self.no_oven.tanggal_selesai_stick
                    self.tanggal_helper_stick = self.no_oven.tanggal_selesai_stick
                    self.tanggal_masuk_oven = self.no_oven.tanggal_masuk_oven
                    self.tanggal_helper_masukoven = self.no_oven.tanggal_masuk_oven
                    self.tanggal_keluar_oven = self.no_oven.tanggal_keluar_oven
                    self.tanggal_helper_keluaroven = self.no_oven.tanggal_keluar_oven


    name = fields.Char(string="No Gudang", default="New")
    tahun = fields.Char(string="Tahun")
    bulan = fields.Char(string="Bulan")
    tujuan_kirim = fields.Char(string="Tujuan Kirim")
    tanggal_in = fields.Date(string="Tanggal In GD KD")
    tanggal_out = fields.Date(string="Tanggal Out GD KD")
    tanggal_selesai_stick = fields.Date(string="Tanggal Selesai Stick")
    tanggal_helper_stick = fields.Date(string="Tanggal Helper Stick")
    tanggal_masuk_oven = fields.Date(string="Tanggal Masuk Oven")
    tanggal_helper_masukoven = fields.Date(string="Tanggal Helper Masuk Oven")
    tanggal_keluar_oven = fields.Date(string="Tanggal Keluar Oven")
    tanggal_helper_keluaroven = fields.Date(string="Tanggal Helper Keluar Oven")
    no_oven = fields.Many2one("kb.mrp.oven")
    keterangan = fields.Text("Keterangan")
    kb_mrp_gudang_kering_ids = fields.One2many('kb.mrp.gudang.kering.line', 'kb_mrp_gudang_kering_id', string="Kb Mrp Gudang Kering Ids")

class kb_mrp_gudang_kering_line(models.Model):
    _name = 'kb.mrp.gudang.kering.line'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_gudang_kering_line, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.gudang.kering.line') or '/'
                rec.name = seq
        return res

    def func_gudang_kering_line_detail(self):
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id('kb_mrp_production.kb_mrp_gudang_kering_line_id')
        return {
            'name': 'Detail',
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'kb.mrp.gudang.kering.line',
            'views': [[form_view_id, 'form']],
            'target': 'new',
            'res_id': self.id,
        }

    def func_ok(self):
        pass

    name = fields.Char(string="No GD KD Line", default="New")
    kb_mrp_gudang_kering_id = fields.Many2one('kb.mrp.gudang.kering', string="No Gudang")
    jenis_kayu = fields.Char(string="Jenis Kayu")
    kode = fields.Char(string="Kode")
    item = fields.Char(string="Item")
    diameter1 = fields.Float(string="Diameter 1")
    diameter2 = fields.Float(string="Diameter 2")
    panjang = fields.Float(string="Panjang")
    log_pakai_pcs = fields.Float(string="Log Pakai PCS")
    log_pakai_m3 = fields.Float(string="Log Pakai M3")
    no_chamber = fields.Char(string="No Chamber")
    kb_mrp_gudang_kering_line_ids = fields.One2many('kb.mrp.gudang.kering.line.detail', 'kb_mrp_gudang_kering_line_id', string="Kb Mrp Gudang Kering Line Detail Ids")
    kb_mrp_oven_line_id = fields.Many2one('kb.mrp.oven.line')

class kb_mrp_gudang_kering_line_detail(models.Model):
    _name = 'kb.mrp.gudang.kering.line.detail'

    @api.model
    def create(self, vals):
        res = super(kb_mrp_gudang_kering_line_detail, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.mrp.gudang.kering.line.detail') or '/'
                rec.name = seq
        return res

    name = fields.Char(string="No Detail GD KD", default="New")
    kb_mrp_gudang_kering_line_id = fields.Many2one('kb.mrp.gudang.kering.line', string="Kb Mrp Gudang Kering Line Id")
    tebal = fields.Float(string="Tebal")
    lebar = fields.Float(string="Lebar")
    panjang = fields.Float(string="Panjang")
    hasil_keping = fields.Float(string="Hasil Keping")
    hasil_m3 = fields.Float(string="Hasil M3")
    shift = fields.Char(string="Shift")
    vakum_celup = fields.Char(string="Vakum / Celup")
    grade = fields.Char(string="Grade")
    fsc = fields.Char(string="FSC")
    kb_mrp_oven_line_detail_id = fields.Many2one('kb.mrp.oven.line.detail')




class mrp_bom(models.Model):
    _inherit = 'mrp.bom'

    # def get_domain_product(self):
    #     # [('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]
    #     self._cr.execute("""(select
    #                             a.id
    #                         from product_template a
    #                         join product_product b on b.product_tmpl_id = a.id
    #                         join kb_mrp_pembahanan c on c.item = b.id
    #                         where (a.company_id is null or a.company_id is not null)
    #                         and a.type in ('product','consu'))""")
    #     fet_product = [x[0] for x in self._cr.fetchall()]
    #     domain = [('id', 'in', fet_product)]
    #     return domain
    #
    #     print(domain)
    #
    #
    # product_tmpl_id = fields.Many2one(
    #     'product.template', 'Product',
    #     check_company=True, index=True,
    #     domain=get_domain_product,
    #     required=True)

class mrp_production(models.Model):
    _inherit = 'mrp.production'

    # def get_domain_product(self):
    #
    #     self._cr.execute("""(select
    #                             y.id
    #                         from product_template x
    #                         join product_product y on y.product_tmpl_id = x.id
    #                         join mrp_bom z on z.product_id = y.id
    #                         where (x.company_id is null or x.company_id is not null)
    #                         and x.type in ('product','consu'))""")
    #     fet_product = [x[0] for x in self._cr.fetchall()]
    #     domain = [('id', 'in', fet_product)]
    #     return domain
    #
    # product_id = fields.Many2one(
    #     'product.product', 'Product',
    #     check_company=True, index=True,
    #     domain=get_domain_product,
    #     required=True)



class kb_mrp_rencana_pemakaian(models.Model):
    _name = 'kb.mrp.rencana.pemakaian'

    name = fields.Char(string='No', default="New")
    tebal = fields.Float(string="Tebal(cm)")
    stock_ad = fields.Float(string="Stock A/D")
    stock_oven = fields.Float(string="Stock Dalam Oven")
    stock_kd = fields.Float(string="Stock K/D")


class stock_move(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        res = super(stock_move, self).write(vals)
        if 'product_sawmil_ids' in vals:
            total = 0
            for line in self.product_sawmil_ids:
                total += line.hasil_m3
            self.quantity_done = total
        return res

    def get_domain_product_sawmil(self):
        for this in self:
            data = []
            if this.raw_material_production_id._origin.id != False:
                self._cr.execute("""(select a.id from kb_mrp_sawmil_line_detail a
                                    join kb_mrp_sawmil_line b on b.id = a.kb_mrp_sawmil_line_id 
                                    join kb_mrp_sawmil c on c.id = b.kb_mrp_sawmil_id 
                                    where c.mo_id = {_mo_id} and a.product_id = {_product}
                )""".format(_mo_id=this.raw_material_production_id._origin.id,_product=this.product_id.id))
                data = [x[0] for x in self._cr.fetchall()]
            this.product_sawmil_helper_ids = [(6,0,data)]

    @api.onchange('product_sawmil_ids')
    def func_onchange_product_sawmil_ids(self):
        total = 0
        for line in self.product_sawmil_ids:
            total += line.hasil_m3
        self.quantity_done = total


    product_sawmil_ids = fields.Many2many('kb.mrp.sawmil.line.detail', 'stock_move_sawmil_detail_rel', 'stock_move_id', 'sawmil_detail_id', string="Product Sawmil Ids")
    product_sawmil_helper_ids = fields.Many2many('kb.mrp.sawmil.line.detail', 'stock_move_sawmil_detail_helper_rel', 'stock_move_id', 'sawmil_detail_id', string="Product Sawmil Helper Ids", compute=get_domain_product_sawmil)

class kb_pallet_sawmil(models.Model):
    _name = 'kb.pallet.sawmil'

    @api.model
    def create(self, vals):
        res = super(kb_pallet_sawmil, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.pallet.sawmil') or '/'
                rec.name = seq
        return res

    @api.onchange('panjang','lebar','tebal')
    def func_onchange_plt(self):
        self.kb_pallet_sawmil_ids = None

    name = fields.Char(string="No Pallet Sawmil", default="New")
    tanggal_pallet = fields.Date(string="Tanggal Pallet")
    panjang = fields.Float(string="Panjang", default=0)
    tebal = fields.Float(string="Tebal", default=0)
    lebar = fields.Float(string="Lebar", default=0)
    kb_pallet_sawmil_ids = fields.One2many('kb.pallet.sawmil.line', 'kb_pallet_sawmil_id', string="Kb Pallet Sawmil Ids")




class kb_pallet_sawmil_line(models.Model):
    _name = 'kb.pallet.sawmil.line'

    @api.model
    def create(self, vals):
        res = super(kb_pallet_sawmil_line, self).create(vals)
        for rec in res:
            if rec.name == "New":
                seq = self.env['ir.sequence'].next_by_code('kb.pallet.sawmil.line') or '/'
                rec.name = seq
        return res


    @api.model
    def get_user_id(self):
        user = self.env.user
        return user.id

    @api.onchange('user_id')
    def func_onchange_user_id(self):
        self.get_sawmil_detail_ids()

    def get_sawmil_detail_ids(self):
        for this in self:
            self._cr.execute("""(select id from kb_mrp_sawmil_line_detail
                where panjang = {_panjang} and lebar = {_lebar} and tebal = {_tebal})""".format(
                _panjang=self.kb_pallet_sawmil_id.panjang, _lebar=self.kb_pallet_sawmil_id.lebar,
                _tebal=self.kb_pallet_sawmil_id.tebal))
            fet = [x[0] for x in self._cr.fetchall()]
            this.sawmil_detail_ids = [(6,0,fet)]

    @api.onchange('sawmil_detail_id')
    def func_onchange_sawmil_detail_id(self):
        if self.sawmil_detail_id.id != False:
            self.location_id = self.sawmil_detail_id.location_id.id
            self.product_id = self.sawmil_detail_id.product_id.id
            self.panjang = self.sawmil_detail_id.panjang
            self.tebal = self.sawmil_detail_id.tebal
            self.lebar = self.sawmil_detail_id.lebar
            self.hasil_keping = self.sawmil_detail_id.hasil_keping
            self.hasil_m3 = self.sawmil_detail_id.hasil_m3
            self.shift = self.sawmil_detail_id.shift
        else:
            self.location_id = None
            self.product_id = None
            self.panjang = 0
            self.tebal = 0
            self.lebar = 0
            self.hasil_keping = 0
            self.hasil_m3 = 0
            self.shift = ""


    name = fields.Char(string="No Pallet Sawmil", default="New")
    kb_pallet_sawmil_id = fields.Many2one('kb.pallet.sawmil', string="No Pallet Sawmil")
    product_id = fields.Many2one('product.product', string="Product")
    panjang = fields.Float(string="Panjang", default=0)
    tebal = fields.Float(string="Tebal", default=0)
    lebar = fields.Float(string="Lebar", default=0)
    hasil_keping = fields.Float(string="Hasil Keping", default=0)
    hasil_m3 = fields.Float(string="Hasil M3", default=0)
    shift = fields.Char(string="Shift")
    location_id = fields.Many2one('stock.location', string="Location Id")
    sawmil_detail_id = fields.Many2one('kb.mrp.sawmil.line.detail', string="Detail Sawmil")
    user_id = fields.Many2one('res.users', default=get_user_id)
    sawmil_detail_ids = fields.Many2many('kb.mrp.sawmil.line.detail', 'pallet_sawmil_detail_rel',
                                         'pallet_sawmil_id', 'sawmil_detail_id', string="Sawmil Detail Ids",
                                         compute=get_sawmil_detail_ids)























