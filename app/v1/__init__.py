from flask_restful import Api
from flask import Blueprint

from .views.apartment_management import *
from .views.user_management import *
from .views.billing import *

from .reports.reports import *
from .views.admin_views import *

# Backend API
from .views.backend_user import *
from .views.backend_apartment import *
from .views.backend_admin import *
from .views.backend_billing import *

version_one = Blueprint('api', __name__)
api = Api(version_one)

api.add_resource(DataUpload,"/data/upload")

api.add_resource(LandingPage,"/")
api.add_resource(DbInitializer,"/restricted")
api.add_resource(RegisterUserGroup,"/add/usergroup")
api.add_resource(DeleteUserGroup,"/remove/usergroup")
api.add_resource(CompanyGroup,"/company/group")
api.add_resource(Users,"/users")
api.add_resource(RegisterUser,"/add/user")
api.add_resource(SignUpCategory,"/signup")
api.add_resource(RequestDemo,"/demo")
api.add_resource(SelfUserRegisterAgent,"/signup/agent")
api.add_resource(SelfUserRegisterOwner,"/signup/owner")
api.add_resource(AdminRegisterUser,"/add/admincreateuser")
api.add_resource(ViewNewClients,"/new/clients")
api.add_resource(ViewClients,"/clients")
api.add_resource(AdminCreateAgent,"/add/admincreateagent")
api.add_resource(Index,"/index")
api.add_resource(Dashboard,"/dashboard")

api.add_resource(MonitorActivity,"/monitor/activityy")
api.add_resource(PropData,"/fetch/propdata")
api.add_resource(PropSearchData,"/fetch/searchdata")
api.add_resource(PropStats,"/fetch/propstats")

api.add_resource(PropOverview,"/get/props")
api.add_resource(HouseOverview,"/get/units")
api.add_resource(TenantOverview,"/get/tenants")
api.add_resource(OccupancyOverview,"/get/occupancy")
api.add_resource(InvoiceOverview,"/get/invoices")
api.add_resource(PaidOverview,"/get/paid")
api.add_resource(BalanceOverview,"/get/balance")
api.add_resource(CollectionOverview,"/get/collection")

api.add_resource(HouseStats,"/fetch/housestats")
api.add_resource(GraphStats,"/fetch/graphstats")
api.add_resource(ComStats,"/fetch/comstats")
api.add_resource(ComGraphStats,"/fetch/comgraphstats")
api.add_resource(UserLogin,"/signin")
api.add_resource(UserLogout,"/logout")
api.add_resource(DeleteUser,"/remove/user")
api.add_resource(UpdateUser,"/update/user")
api.add_resource(AssignRole,"/assign/role")
api.add_resource(ModifyAccessRight,"/modify/access")

api.add_resource(CreateLocation,"/add/location")
api.add_resource(RegisterOwner,"/add/owner")
api.add_resource(CreateApartment,"/add/apartment")
api.add_resource(Bills,"/bills")
api.add_resource(DiscardBills,"/discard/bills")
api.add_resource(Payments,"/all/payments")
api.add_resource(PropertyManagement,"/manage/property")
api.add_resource(MeterManagement,"/meters")
api.add_resource(SubmissionsManagement,"/submissions")
api.add_resource(PaymentsManagement,"/manage/payments")
api.add_resource(UpdateCompanyDetails,"/update/companyinfo")
api.add_resource(PropertyImageChange,"/change/prop/image")
api.add_resource(UpdatePropertyDetails,"/update/propinfo")
api.add_resource(PropertyAccess,"/property/access")
api.add_resource(PropertyAccessTermination,"/property/termination")
api.add_resource(Expenses,"/expenses")
api.add_resource(ExpenseManagement,"/expense/management")

api.add_resource(BulkSms,"/bulk/sms")
api.add_resource(FetchSentSms,"/fetch/sentsms")
api.add_resource(SendInvoices,"/send/invoices")
api.add_resource(SendMail,"/send/mail")
api.add_resource(SendSms,"/send/sms")
api.add_resource(TenantSms, "/tenant/sms")
api.add_resource(CreateHouseCode,"/create/housecode")
api.add_resource(EditHouseCode,"/edit/housecode")
api.add_resource(CreateHouse, "/add/house")
api.add_resource(EditHouse, "/edit/house")
api.add_resource(HouseBillStatus, "/bill/status")
api.add_resource(TenantSmsStatus, "/sms/status")
api.add_resource(SmsDelivery, "/sms/delivery")
api.add_resource(CreateMeter, "/add/meter")
api.add_resource(UpdateMeter,"/edit/meter")
api.add_resource(AllocateMeters,"/allocate/meter")
api.add_resource(MeterRemoval,"/clear/meter")

# api.add_resource(StandardRates,"/create/standardrates")
api.add_resource(SalesRepsManagement,"/reps/management")
api.add_resource(CaptureReading, "/readings")
api.add_resource(CreateWaterCharge, "/create/waterbills")
api.add_resource(EditReading,"/edit/readings")
api.add_resource(TenantHouseRequest,"/tenant/request")
api.add_resource(HouseClearanceRequest,"/clear/request")
api.add_resource(HouseTransferRequest,"/transfer/request")
api.add_resource(ContactManagement,"/tenant/message")
api.add_resource(HandleTenantRequest,"/handle/request")
api.add_resource(ReactToRequest,"/request/respond")
api.add_resource(TrackRequest,"/track/request")
api.add_resource(DeleteRequest,"/delete/request")
api.add_resource(AddTenant,"/add/tenant")
api.add_resource(Deal,"/deal")
api.add_resource(AddSalesAgent,"/sales/agent")
api.add_resource(TenantManagement,"/tenants")
api.add_resource(UpdateTenant,"/update/tenant")
api.add_resource(AllocateTenants,"/allocate/tenant")
api.add_resource(TenantClearance,"/clear/tenant")
api.add_resource(TenantUserSignUpStageOne,"/tenant/signup")
api.add_resource(TenantUserSignUpStageTwo,"/tenant/signuptwo")
api.add_resource(CheckVacancy,"/search/house")
api.add_resource(RentRemit,"/remit/data")


api.add_resource(Settings, "/settings")
api.add_resource(Search, "/search")


api.add_resource(Results, "/results")


api.add_resource(Billing, "/billing")
api.add_resource(BillProgress, "/bill/progress")
api.add_resource(SwitchPeriod,"/switch")
api.add_resource(Replenish,"/replenish")
api.add_resource(ReplenishAll,"/replenish/forceall")

api.add_resource(ClientBilling,"/client/billing")
api.add_resource(SetReminder,"/set/reminder")
api.add_resource(AmendCharge,"/amend/charge")
api.add_resource(EditBill,"/edit/bill")
api.add_resource(EditSummary,"/edit/summary")
api.add_resource(ReceivePayment,"/receive/payment")
api.add_resource(UploadPayments,"/upload/payments")
api.add_resource(ReceiveDepositPayment,"/deposit/payment")
api.add_resource(TenantPayment,"/tenant/payment")
api.add_resource(StkCallBackUrlProminance,"/datareceive")
api.add_resource(StkCallBackUrlKiotapay,"/kiotapay/datareceive")
api.add_resource(StkCallBackUrlAstrol,"/stk/astrol/ins/payment")
api.add_resource(ResultUrl,"/getdata/<int:shortcode>")
api.add_resource(TestApi,"/testapi")
api.add_resource(QueryMpesaTrans,"/query")
api.add_resource(ConsumeMpesaData,"/mpesa/payment")
api.add_resource(ResetAllMpesaData,"/restricted/datareset")

#c2b urls
api.add_resource(CallBackUrlProminance,"/promitech/payment")
api.add_resource(CallBackUrlKiotapay,"/kiotapay/payment")
api.add_resource(CallBackUrlLatitude,"/latitude/payment") # to be deprecated
api.add_resource(CallBackUrlMLatitude,"/m/latitude/ins/payment")
api.add_resource(CallBackUrlPremier,"/premier/payment")
api.add_resource(CallBackUrlVintage,"/vintage/payment")
api.add_resource(CallBackUrlPremierRealty,"/prealty/payment")
api.add_resource(CallBackUrlAstrol,"/m/astrol/ins/payment")
api.add_resource(CallBackUrlAstrolRuiru,"/m/astrolruiru/ins/payment")
api.add_resource(CallBackUrlDenvic,"/m/denvic/ins/payment")
api.add_resource(CallBackUrlDenvicTwo,"/m/denvictwo/ins/payment")
api.add_resource(CallBackUrlDenvicThree,"/m/denvicthree/ins/payment")
api.add_resource(CallBackUrlBizlineBaraka,"/m/bizlinebaraka/ins/payment")
api.add_resource(CallBackUrlGoldLabel,"/m/goldlabel/ins/payment")
api.add_resource(CallBackUrlBizlineBestel,"/m/bizlinebestel/ins/payment")
api.add_resource(CallBackUrlBizlineNeema,"/m/bizlineneema/ins/payment")
api.add_resource(CallBackUrlLagad,"/m/lagad/ins/payment")
api.add_resource(CallBackUrlImani,"/m/kalinaw/ins/payment")


api.add_resource(CallBackUrlAssetisha,"/api/ins/confirm")
api.add_resource(RentNaiveraStatement,"/report/fetch/<string:id_number>/<string:month>/-/<string:year>/<string:prop>")
api.add_resource(LandlordIncomeWallet,"/api/landlord/account/<int:id_number>")
# api.add_resource(Assetisha,"api/landlord/statement/<int:id_number>")

api.add_resource(AgentWallet,"/api/agent/account/<int:id_number>")
api.add_resource(AgentWithdrawal,"/api/agent/withdraw/request")
api.add_resource(AgentWithdrawalConfirmation,"/api/ins/agent/withdraw/confirm")
api.add_resource(HouseData,"/api/unit/data/<string:user_id>/<string:unit_number>")

#bank urls
api.add_resource(CallBackUrlEquity,"/nest/payment")
api.add_resource(CallBackUrlEquityProd,"/promitech/4012401")

api.add_resource(CallBackUrlLatitudeEquity,"/latitude/payment")
api.add_resource(CallBackUrlTestLatitudeEquity,"/test/latitude/payment")

api.add_resource(CallBackUrlSentomEquity,"/b/sentom/ins/payment")
api.add_resource(CallBackUrlTestSentomEquity,"/b/sentom/ins/testpayment")

api.add_resource(CallBackUrlLymaxEquity,"/bank/lymax/prod")
api.add_resource(CallBackUrlTestLymaxEquity,"/bank/lymax/test")

api.add_resource(CallBackUrlCherahEquity,"/bank/cherah/prod")
api.add_resource(CallBackUrlTestCherahEquity,"/bank/cherah/test")

api.add_resource(CallBackUrlMerit,"/bank/merit/prod")
api.add_resource(CallBackUrlTestMerit,"/bank/merit/test")

api.add_resource(CallBackUrlLes,"/les/45")
api.add_resource(CallBackUrlTestLes,"/test/les/45")

api.add_resource(ViewHouses, "/view/houses")
api.add_resource(ViewMeters, "/view/meters")

api.add_resource(ViewBookings, "/view/bookings")
api.add_resource(ViewTenancy, "/view/tenancy")
api.add_resource(ViewTenantInfo,"/view/tenantinfo")
api.add_resource(ViewTenantDetail, "/view/tenantdetail")
api.add_resource(ViewTenantDetailTwo,"/view/tenantdetailtwo")
api.add_resource(ViewVacatedTenants, "/view/vacatedtenants")

api.add_resource(ViewMonthlyReading, "/view/monthlyreadings")
api.add_resource(ViewWaterCharge, "/view/watercharge")
api.add_resource(ViewPayment, "/view/payments")
api.add_resource(ViewMonthlyPayments,"/view/monthlypayment")

api.add_resource(GetStarted,"/get/started")
api.add_resource(ContactUs,"/contact")
api.add_resource(Features,"/features")
api.add_resource(AboutUs,"/about/us")
api.add_resource(Pricing,"/pricing")
api.add_resource(ReportBug,"/report/bug")
api.add_resource(ViewBugs, "/view/bugs")

api.add_resource(Invoice,"/invoice")
api.add_resource(BillInvoice,"/bill/invoice")
api.add_resource(ClientInvoice,"/client/invoice")
api.add_resource(MyPayments,"/payments")
api.add_resource(Receipt,"/receipt")
api.add_resource(UpdateBalance,"/update/balance")
api.add_resource(EditPayment,"/edit/payment")

api.add_resource(Reports,"/reports")
api.add_resource(ReportsThree,"/reports/3")
api.add_resource(Balances,"/balances")
api.add_resource(BalanceReport,"/balance/report")
api.add_resource(RentReport,"/rent/report")
api.add_resource(MonthlyStatement,"/monthly/statement")
api.add_resource(SummarisedCombinedBill,"/summarised/combinedbill")
api.add_resource(ExternalDetail,"/external/detailed")
api.add_resource(CombinedReportSummary,"/combinedreport/summary")
api.add_resource(CombinedReport,"/combined/report")

api.add_resource(CustomCombinedReport,"/customcombined/report")

api.add_resource(RentStatement,"/rent/statement")
api.add_resource(DepositStatement,"/deposit/statement")
api.add_resource(ServiceStatement,"/service/statement")
api.add_resource(WaterStatement,"/water/statement")
api.add_resource(ListedProperties,"/listed/properties")
api.add_resource(GarbageStatement,"/garbage/statement")
api.add_resource(LPFStatement,"/lpf/statement")
api.add_resource(InternalSummary,"/internal/summarised")
api.add_resource(InternalDetail,"/internal/detailed")
api.add_resource(InternalDetailAlt,"/general/statement")
api.add_resource(TenantStatement,"/tenant/statement")
api.add_resource(TenantStatementTwo,"/tenant/statement2")
api.add_resource(TenantStatementThree,"/tenant/statement3")
api.add_resource(StatementOfAccounts,"/account/statement")
api.add_resource(BookingSchedule,"/booking/schedule")
api.add_resource(MpesaStatement,"/mpesa/statement")
api.add_resource(MeritStatementOne,"/st/one")

api.add_resource(TenantListing,"/tenant/listing")
api.add_resource(TenantStatementFour,"/tenant/statement4")

api.add_resource(CollectionRatioReport,"/cr/report")
# api.add_resource(ManagementFeeReport,"/commission/report")
api.add_resource(OfficePnL,"/profitnloss/report")
api.add_resource(OfficeExpenses,"/office/expenses")
api.add_resource(CustomReport,"/custom/report")
api.add_resource(RemitStatement,"/remit/statement")


api.add_resource(ExpenseDetail,"/expenses/detailed")
api.add_resource(SubmissionsReport,"/submissions/report")

api.add_resource(ArrearsComparison,"/arrears")
api.add_resource(PaymentsComparison,"/compare/payments")

api.add_resource(FetchTenants,"/fetch/tenants")
api.add_resource(FetchHouses,"/fetch/houses")
api.add_resource(FetchRates,"/fetch/rates")
api.add_resource(FetchMeters,"/fetch/meters")
api.add_resource(FetchReadings,"/fetch/readings")
api.add_resource(FetchPayments,"/fetch/payments")
api.add_resource(FetchSubmissions,"/fetch/submissions")
api.add_resource(FetchBills,"/fetch/bills")
api.add_resource(FetchAgents,"/fetch/agents")
api.add_resource(FetchUsers,"/fetch/users")


api.add_resource(Privacy,"/privacy")

# ADMIN ROUTES
api.add_resource(AllProperties,"/all/properties")
api.add_resource(AddProp,"/add/prop")
api.add_resource(AddOwner,"/add/propowner")
api.add_resource(AllOwners,"/all/owners")
api.add_resource(AddRegion,"/add/region")
api.add_resource(LinkProperty,"/link/prop")
api.add_resource(EditProp,"/edit/prop")
api.add_resource(LandlordDemoLogin,"/demo/kp0716674695mp0725538750landlord")
api.add_resource(DemoLogin,"/demo/dxjnc5a3s")
api.add_resource(TenantDemoLogin,"/demo/kp0716674695mp0725538750tenant")
api.add_resource(DemoAccess,"/trial/<string:ri>")
api.add_resource(Demo,"/demo/abtytbhvgcfxnbh")


# api.add_resource(Robots,"/robots")
api.add_resource(Robots,"/robots.txt")
api.add_resource(ViewReceipt,"/r/<string:ri>")
api.add_resource(QueryResident,"/query/<string:ri>")

api.add_resource(UserActivation,"/user/<string:ri>")

api.add_resource(DownloadReceipt,"/download/receipt/<string:ri>")
api.add_resource(DownloadInvoice,"/download/invoice/<string:ri>")
api.add_resource(DeleteReceipt,"/del/r/prop/<string:propid>")

api.add_resource(DownloadTemplate,"/download/template/<string:file>")



api.add_resource(FetchExcel,"/fetch/excel")
api.add_resource(FetchPdf,"/fetch/pdf")
# ADMIN FRONTEND API
#api.add_resource(UserLogin,"/signin")
api.add_resource(BUserLogin,"/auth")
api.add_resource(BUserLogout,"/blogout")
api.add_resource(BComStats,"/fetch/bcomstats")
api.add_resource(BComGraphStats,"/fetch/bcomgraphstats")
# api.add_resource(BAdminRegisterUser,"/add/badmincreateuser")
api.add_resource(BRegisterOwner,"/add/bowner")
api.add_resource(BAllOwners,"/all/bowners")
api.add_resource(BUpdateUser,"/update/buser")
api.add_resource(BCreateApartment,"/add/bapartment")
api.add_resource(BAdminCreateAgent,"/add/badmincreateagent")
api.add_resource(BModifyAccessRight,"/modify/baccess")
api.add_resource(BRegisterUser,"/add/buser")
api.add_resource(BPropertyAccess,"/property/baccess")
api.add_resource(BPropertyAccessTermination,"/property/btermination")
api.add_resource(BAddProp,"/add/bprop")

api.add_resource(BAllProperties,"/all/bproperties")
api.add_resource(BClientBilling,"/client/bbilling")
api.add_resource(BBilling, "/bbilling")
api.add_resource(BMpesa, "/bmpesa")

api.add_resource(BRegisterUserGroup,"/add/busergroup")
api.add_resource(BAssignRole,"/assign/brole")