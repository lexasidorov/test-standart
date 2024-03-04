from sqlalchemy import ForeignKey, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

PAYMENT_TYPE_CARD = 0
PAYMENT_TYPE_ACCOUNT = 1
IS_CREDIT = False
INVOICE_STATUS_WAIT = 1
INVOICE_STATUS_PAYED = 2
INVOICE_STATUS_CANCELED = 0
IS_ADMIN = False


class Base(DeclarativeBase):
    pass


class Requisites(Base):
    __tablename__ = 'requisites_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_type: Mapped[int] = mapped_column(default=PAYMENT_TYPE_CARD)
    is_credit: Mapped[bool] = mapped_column(default=IS_CREDIT)
    fio: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50))
    limit: Mapped[int] = mapped_column(default=0)

    # Parent -> Requisites
    # Child -> Invoices
    invoices: Mapped[list["Invoices"]] = relationship(back_populates="requisites")

    def __repr__(self) -> str:
        return f"Requisites(id={self.id!r}" \
               f"is_credit: {self.is_credit!r}, fio={self.fio!r}, " \
               f"phone_number: {self.phone_number!r})"


class Invoices(Base):
    __tablename__ = 'invoices_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    sum: Mapped[int] = mapped_column(Float(50), nullable=False)
    status: Mapped[int] = mapped_column(default=INVOICE_STATUS_WAIT, nullable=False)

    # parent -->
    requisites_id: Mapped[int] = mapped_column(ForeignKey("requisites_table.id"))
    requisites: Mapped["Requisites"] = relationship(back_populates="invoices")

    def __repr__(self) -> str:
        return f"Invoices(id={self.id}, sum={self.sum}, status: {self.status}, requisites: {self.requisites})"


class Users(Base, UserMixin):
    __tablename__ = 'users_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[bool] = mapped_column(default=IS_ADMIN, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)

    def __repr__(self) -> str:
        return f"Users(id={self.id!r}, login={self.login!r}, role={self.role!r}"

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)
