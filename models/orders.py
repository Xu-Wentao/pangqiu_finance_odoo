# -*- coding: UTF-8 -*-
from decimal import Decimal

from odoo import fields, api, models


class YeChaoOrders(models.Model):
    _name = 'yc.orders'

    goods_no = fields.Char('商品编号')
    order_no = fields.Char('订单号')
    buyer_nick_name = fields.Char('买家昵称')
    seller_open_id = fields.Char('卖家openid')
    receiver_name = fields.Char('收货人')
    receiver_phone = fields.Char('收货人电话')
    receiver_address = fields.Char('收货人地址')
    goods_name = fields.Char('商品名')
    goods_desc = fields.Text('商品描述')
    ball_num = fields.Char('球数')
    logistics_type = fields.Char('物流方式')
    logistics_cost = fields.Char('应付物流费')
    logistics_payed = fields.Char('实付物流费')
    logistics_status = fields.Char('物流费状态')
    create_time = fields.Datetime('创建时间')
    order_type = fields.Char('订单类型')
    sent = fields.Char('是否发货')
    order_person = fields.Char('下单人')
    channel = fields.Char('渠道')
    channel_no = fields.Char('渠道订单号')
    price = fields.Char('渠道金额')
    logistics_company = fields.Char('快递公司')
    logistics_no = fields.Char('运单号')
    remark = fields.Char('备注')
    finance_remark = fields.Char('财务备注')
    checked = fields.Boolean(default=False, string='已比对')
    alipay_id = fields.Many2one('yc.orders_alipay', string='支付宝订单')

    @api.model
    def create(self, vals):
        if vals.get('channel_no', False):
            vals['channel_no'] = vals['channel_no'].replace(' ', '')
        if vals.get('order_no', False):
            vals['order_no'] = vals['order_no'].replace(' ', '')
        return super(YeChaoOrders, self).create(vals)


class YeChaoOrdersUpdate(models.Model):
    _name = 'yc.orders_update'

    order_no = fields.Char('订单号', required=True)
    channel = fields.Char('渠道')
    channel_no = fields.Char('渠道订单号')
    price = fields.Char('渠道金额')
    logistics_company = fields.Char('快递公司')
    logistics_no = fields.Char('运单号')
    finance_remark = fields.Char('财务备注')

    @api.model
    def create(self, vals):
        if vals.get('channel_no', False):
            vals['channel_no'] = vals['channel_no'].replace(' ', '')
        if vals.get('order_no', False):
            vals['order_no'] = vals['order_no'].replace(' ', '')
        return super(YeChaoOrdersUpdate, self).create(vals)

    @api.multi
    def update_orders(self):
        for record in self:
            try:
                order = self.env['yc.orders'].search(
                    [('order_no', '=', record.order_no)])[0]
                update_dict = ['channel', 'channel_no', 'price',
                               'logistics_company', 'logistics_no',
                               'finance_remark']
                update_values = {}
                for field in update_dict:
                    if record[field]:
                        if field == 'channel_no':
                            update_values[field] = int(record[field])
                        else:
                            update_values[field] = record[field]
                order.update(update_values)
                record.unlink()
            except:
                pass


class YechaoOrdersAlipay(models.Model):
    _name = 'yc.orders_alipay'

    alipay_no = fields.Char('支付宝订单号')
    pay_account = fields.Char('付款账号')
    channel_no = fields.Char('渠道订单号')
    price = fields.Char('金额')
    time = fields.Date('日期')
    order_ids = fields.One2many('yc.orders', 'alipay_id', '订单')
    checked = fields.Boolean(default=False, string='已比对')
    diff = fields.Selection([('0', '相同'), ('1', '错误')], string='核对结果')
    order_price_sum = fields.Char('订单合计金额')
    remark = fields.Char('备注')

    @api.model
    def create(self, vals):
        if vals.get('channel_no', False):
            vals['channel_no'] = vals['channel_no'].replace(' ', '')
        return super(YechaoOrdersAlipay, self).create(vals)

    @api.multi
    def check(self):
        for record in self:
            orders = self.env['yc.orders'].search(
                [('channel_no', '=', int(record.channel_no))])
            order_ids = []
            order_price_sum = Decimal()
            if orders:
                for order in orders:
                    order_ids.append(order.id)
                    try:
                        order_price_sum += Decimal(order.price)
                        order.checked = True
                    except:
                        pass
                record.order_ids = [(6, 0, order_ids)]
                record_price = Decimal()
                try:
                    record_price = Decimal(record.price)
                except:
                    pass
                if record_price == order_price_sum:
                    record.diff = '0'
                else:
                    record.diff = '1'
                record.checked = True
                record.order_price_sum = order_price_sum
