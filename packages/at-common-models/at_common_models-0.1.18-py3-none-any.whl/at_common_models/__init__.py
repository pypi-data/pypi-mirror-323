# Import all models to register them with SQLAlchemy
from at_common_models.stock.overview import OverviewModel
from at_common_models.stock.daily_candlestick import DailyCandlestickModel
from at_common_models.stock.daily_indicator import DailyIndicatorModel
from at_common_models.stock.quotation import QuotationModel
from at_common_models.stock.financials.annual_balance_sheet_statement import AnnualBalanceSheetStatementModel
from at_common_models.stock.financials.quarter_balance_sheet_statement import QuarterBalanceSheetStatementModel
from at_common_models.stock.financials.annual_income_statement import AnnualIncomeStatementModel
from at_common_models.stock.financials.quarter_income_statement import QuarterlyIncomeStatementModel
from at_common_models.stock.financials.annual_cashflow_statement import AnnualCashFlowStatementModel
from at_common_models.stock.financials.quarter_cashflow_statement import QuarterCashflowStatementModel
from at_common_models.news.article import NewsArticleModel
from at_common_models.news.stock import NewsStockModel
from at_common_models.system.task import TaskModel
from at_common_models.system.workflow import WorkflowModel
from at_common_models.system.prompt import PromptModel
from at_common_models.user.account import UserAccount
from at_common_models.user.oauth import UserOAuth
from at_common_models.user.subscription import UserSubscription
from at_common_models.base import BaseModel

# These imports will register all models with the Base.metadata
__all__ = [
    'BaseModel',
    'OverviewModel',
    'DailyCandlestickModel',
    'DailyIndicatorModel',
    'QuotationModel',
    'AnnualBalanceSheetStatementModel',
    'QuarterBalanceSheetStatementModel',
    'AnnualIncomeStatementModel',
    'QuarterlyIncomeStatementModel',
    'AnnualCashFlowStatementModel',
    'QuarterCashflowStatementModel',
    'NewsArticleModel',
    'NewsStockModel',
    'TaskModel',
    'PromptModel',
    'WorkflowModel',
    'UserAccount',
    'UserOAuth',
    'UserSubscription'
]
