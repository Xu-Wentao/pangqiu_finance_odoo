# -*- coding: UTF-8 -*-
from decimal import Decimal

from odoo import fields, api, models


class QMallOrders(models.Model):
    _name = 'qmall.orders'

    vendor_name = fields.Char('供应商名称')
    order_no = fields.Char('订单编号')
    pay_no = fields.Char('支付单号')
    order_created_at = fields.Char('下单时间')
    user = fields.Char('用户')
    user_phone = fields.Char('手机号码')
    province = fields.Char('省')
    city = fields.Char('市')
    district = fields.Char('区')
    address_detail = fields.Char('详细地址')
    goods_name = fields.Char('商品名称')
    goods_attributes = fields.Char('商品销售属性')
    goods_num = fields.Char('数量')
    cost_price = fields.Char('成本价')
    goods_price = fields.Char('商品金额')
    pay_price = fields.Char('支付金额')
    logistics_price = fields.Char('运费')
    logistics_company = fields.Char('物流公司')
    logistics_no = fields.Char('物流单号')
    order_status = fields.Char('订单状态')
    channel = fields.Char('渠道')
    channel_no = fields.Char('渠道订单号')
    channel_price = fields.Char('渠道金额')
    order_finished_at = fields.Char('交易完成时间')
    points_rate = fields.Char('扣点比例')
    points_price = fields.Char('扣点金额')
    refund_price = fields.Char('退款金额')
    logistcs_upload = fields.Char('物流上传')
    refund = fields.Char('退款')
    datetime = fields.Char('日期')



class QMallOrdersUpdate(models.Model):
    _name = 'qmall.orders_update'

    order_no = fields.Char('订单编号', required=True)
    channel = fields.Char('渠道')
    channel_no = fields.Char('渠道订单号')
    channel_price = fields.Char('渠道金额')
    logistics_company = fields.Char('物流公司')
    logistics_no = fields.Char('物流单号')

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
                order = self.env['qmall.orders'].search(
                    [('order_no', '=', record.order_no)])[0]
                update_dict = ['channel', 'channel_no', 'price',
                               'logistics_company', 'logistics_no']
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

class QMallOrdersAlipay(models.Model):
    _name = 'qmall.orders_alipay'

    alipay_no = fields.Char('支付宝订单号')
    pay_account = fields.Char('付款账号')
    channel_no = fields.Char('渠道订单号')
    price = fields.Char('金额')
    time = fields.Date('日期')
    order_ids = fields.One2many('qmall.orders', 'alipay_id', '订单')
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
            orders = self.env['qmall.orders'].search(
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
