class Lims(Model):

    id = Column(types.Integer, primary_key=True)
    internal_id = Column(types.String(32), unique=True, nullable=False)
    name = Column(types.String(128), nullable=False)
    priority = Column(types.Enum('diagnostic', 'research'))
    scout_access = Column(types.Boolean, nullable=False, default=False)

    agreement_date = Column(types.DateTime)
    agreement_registration = Column(types.String(32))
    project_account_ki = Column(types.String(32))
    project_account_kth = Column(types.String(32))
    organisation_number = Column(types.String(32))
    invoice_address = Column(types.Text, nullable=False)
    invoice_reference = Column(types.String(32), nullable=False)
    uppmax_account = Column(types.String(32))
    primary_contact = Column(types.String(128))
    delivery_contact = Column(types.String(128))
    invoice_contact = Column(types.String(128))
    customer_group_id = Column(ForeignKey('customer_group.id'), nullable=False)

    families = orm.relationship('Family', backref='customer', order_by='-Family.id')
    samples = orm.relationship('Sample', backref='customer', order_by='-Sample.id')
    pools = orm.relationship('Pool', backref='customer', order_by='-Pool.id')
    orders = orm.relationship('MicrobialOrder', backref='customer', order_by='-MicrobialOrder.id')

    def __str__(self) -> str:
        return f"{self.internal_id} ({self.name})"