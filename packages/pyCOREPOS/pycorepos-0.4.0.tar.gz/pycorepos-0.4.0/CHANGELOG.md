
# Changelog
All notable changes to pyCOREPOS will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.4.0 (2025-01-24)

### Feat

- add common base class for `dtransactions` and similar models

### Fix

- add `Employee` model for lane_op
- fix ordering of name columns for MemberInfo

## v0.3.5 (2025-01-15)

### Fix

- add workaround to avoid missing schema columns

## v0.3.4 (2025-01-15)

### Fix

- misc. cleanup for sales batch models
- add more enums for batch discount type, editor UI

## v0.3.3 (2025-01-13)

### Fix

- remove `autoincrement` option for composite PK fields

## v0.3.2 (2025-01-11)

### Fix

- add base class for all transaction tables, views
- add `MemberType.ignore_sales` column
- add model for `MasterSuperDepartment`

## v0.3.1 (2024-12-17)

### Fix

- add `wicable`, `active` columns for Department model

## v0.3.0 (2024-08-06)

### Feat

- add model for `MemberContactPreference` (`op.memContactPrefs`)
- add model for `CustomReceiptLine` (`op.customReceipt`)

## v0.2.1 (2024-07-04)

### Fix

- add API methods, `get_employees()` and `get_employee()`
- remove `Change` data model
- remove dependency for `six` package

## v0.2.0 (2024-06-10)

### Feat

- switch from setup.cfg to pyproject.toml + hatchling

## [0.1.20] - 2024-05-29
### Changed
- Add enum for CORE (Office) DB types.

## [0.1.19] - 2023-11-01
### Changed
- Fix data types for tax, voided in `dtransactions`.
- Fix synonym for `dtransactions.tax`.

## [0.1.18] - 2023-10-12
### Changed
- Fix the `Department.tax_rate` relationship.
- Let `MemberInfo.dates` be an object, not a list.

## [0.1.17] - 2023-10-07
### Changed
- Rename module to `corepos.db.office_arch`.

## [0.1.16] - 2023-09-15
### Changed
- Add model for `office_op.Tender`.

## [0.1.15] - 2023-09-13
### Changed
- Add model for `CustomerNotifications` table.

## [0.1.14] - 2023-09-07
### Changed
- Tweak primary key for StockPurchase model.

## [0.1.13] - 2023-09-02
### Changed
- Add models for StockPurchase and EquityLiveBalance.

## [0.1.12] - 2023-06-12
### Changed
- Add `get_member_types()` method for CORE API.
- Rename model for `custdata` to `CustomerClassic`.
- Add note about `meminfo.email_2` field, aka. "alt. phone".

## [0.1.11] - 2023-06-02
### Changed
- Add support for htdigest auth when using CORE webservices API.

## [0.1.10] - 2023-05-17
### Changed
- Replace `setup.py` contents with `setup.cfg`.

## [0.1.9] - 2023-05-01
### Changed
- Require SQLAlchemy 1.4.x.

## [0.1.8] - 2023-01-02
### Changed
- Add basic `TransactionDetail` for trans archive model.
- Delete `productUser` record when `products` record is deleted.

## [0.1.7] - 2022-03-02
### Changed
- Remove deprecation warning for `corepos.db`.
- Add model for `UserGroup`.

## [0.1.6] - 2021-11-04
### Changed
- Add `User` model for office_op.
- Add proper support for `str(Suspension)`.
- Add the `custdata` model for lane_op DB.

## [0.1.5] - 2021-08-31
### Changed
- Add lane_op model for Department.

## [0.1.4] - 2021-08-02
### Changed
- Add schema for `TableSyncRules`.

## [0.1.3] - 2021-07-21
### Changed
- Add basic 'lane_op' DB schema.

## [0.1.2] - 2021-06-11
### Changed
- Several more updates, mostly a "save point" release.

## [0.1.1] - 2020-09-16
### Added
- A ton of updates, mostly a "save point" release.

## [0.1.0] - 2020-02-27
### Added
- Initial version of the package; defines some basic table mappings.
