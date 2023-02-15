dataset_name_to_metric = {
    "bbcnews": "accuracy",
    "sst2": "accuracy",
    "imdb_genre_prediction": "roc_auc",
    "sst5": "accuracy",
    "product_sentiment_machine_hack": "accuracy",
    "google_qa_answer_type_reason_explanation": "r2",
    "google_qa_question_type_reason_explanation": "r2",
    "bookprice_prediction": "r2",
    "goemotions": "jaccard",
    "jc_penney_products": "r2",
    "fake_job_postings2": "roc_auc",
    "data_scientist_salary": "accuracy",
    "news_popularity2": "r2",
    "women_clothing_review": "r2",
    "ae_price_prediction": "r2",
    "news_channel": "accuracy",
    "jigsaw_unintended_bias100K": "roc_auc",
    "ames_housing": "r2",
    "mercedes_benz_greener": "r2",
    "mushroom_edibility": "accuracy",
    "amazon_employee_access_challenge": "roc_auc",
    "naval": "r2",
    "sarcos": "r2",
    "protein": "r2",
    "adult_census_income": "accuracy",
    "otto_group_product": "accuracy",
    "santander_customer_satisfaction": "accuracy",
    "amazon_employee_access": "roc_auc",
    "numerai28pt6": "accuracy",
    "bnp_claims_management": "accuracy",
    "allstate_claims_severity": "r2",
    "santander_customer_transaction": "accuracy",
    "connect4": "accuracy",
    "forest_cover": "accuracy",
    "ieee_fraud": "accuracy",
    "porto_seguro_safe_driver": "accuracy",
    "walmart_recruiting": "accuracy",
    "poker_hand": "accuracy",
    "higgs": "accuracy",
}


dataset_name_to_repo_name = {
    "ames_housing": "Ames Housing Benchmarks",
    "mercedes_benz_greener": "Mercedes Benz Greener Benchmarks",
    "naval": "Naval Benchmarks",
    "adult_census_income": "Adult Census Income Benchmarks",
    "sarcos": "Sarcos Benchmarks",
    "protein": "Protein Benchmarks",
    "numerai28pt6": "Numerai28pt6 Benchmarks",
    "mushroom_edibility": "Mushroom Edibility Benchmarks",
    "amazon_employee_access_challenge": "Amazon Employee Access Challenge Benchmarks",
    "forest_cover": "Forest Cover Benchmarks",
    "santander_customer_satisfaction": "Santander Customer Satisfaction Benchmarks",
    "connect4": "Connect4 Benchmarks",
    "allstate_claims_severity": "Allstate Claims Severity Benchmarks",
    "santander_customer_transaction": "Santander Customer Transaction Benchmarks",
    "otto_group_product": "Otto Group Product Benchmarks",
    "bbcnews": "BBC News Benchmarks",
    "sst2": "SST2 Benchmarks",
    "imdb_genre_prediction": "IMDB Genre Prediction Benchmarks",
    "sst5": "SST5 Benchmarks",
    "product_sentiment_machine_hack": "Product Sentiment Machine Hack Benchmarks",
    "bookprice_prediction": "Book Price Prediction Benchmarks",
    "goemotions": "GoEmotions Benchmarks",
    "jc_penney_products": "JCPenny Products Benchmarks",
    "fake_job_postings2": "Fake Job Postings Benchmarks",
    "data_scientist_salary": "Data Scientist Salary Benchmarks",
    "news_popularity2": "News Popularity Benchmarks",
    "women_clothing_review": "Women Clothing Review Benchmarks",
    "ae_price_prediction": "AE Price Prediction Benchmarks",
    "news_channel": "News Channel Benchmarks",
    "jigsaw_unintended_bias100K": "Jigsaw Unintended Bias 100K Benchmarks",
    "ieee_fraud": "IEEE Fraud Benchmarks",
    "higgs": "Higgs Benchmarks",
    "titanic": "Titanic Benchmarks",
    "ohsumed_7400": "OHSUMED 7400 Benchmarks",
    "reuters_r8": "Reuters R8 Benchmarks",
    "mercari_price_suggestion100K": "Mercari Price Suggestion 100K Benchmarks",
    "melbourne_airbnb": "Melbourne AirBnb Benchmarks",
    "yelp_review_polarity": "Yelp Review Polarity Benchmarks",
    "yelp_reviews": "Yelp Reviews Benchmarks",
    "amazon_review_polarity": "Amazon Review Polarity Benchmarks",
    "amazon_reviews": "Amazon Reviews Benchmarks",
    "agnews": "AG News Benchmarks",
    "california_house_price": "California House Price Benchmarks",
    "ethos_binary": "Ethos Binary Benchmarks",
    "wine_reviews": "Wine Reviews Benchmarks",
    "yahoo_answers": "Yahoo Answers Benchmarks",
    "google_qa_answer_type_reason_explanation": "Google QAA Benchmarks",
    "google_qa_question_type_reason_explanation": "Google QAQ Benchmarks",
    "bnp_claims_management": "BNP Claims Management",
    "creditcard_fraud": "Credit Card Fraud Benchmarks",
    "imbalanced_insurance": "Imbalanced Insurance Benchmarks",
    "walmart_recruiting": "Walmart Recruiting Benchmarks",
}

dataset_name_to_use_case = {
    "ames_housing": "real estate",
    "mercedes_benz_greener": "industrial",
    "naval": "industrial",
    "adult_census_income": "income prediction",
    "sarcos": "robotics",
    "protein": "biology",
    "numerai28pt6": "financial services",
    "mushroom_edibility": "biology",
    "amazon_employee_access_challenge": "human resources",
    "forest_cover": "biology",
    "santander_customer_satisfaction": "financial services",
    "connect4": "gaming",
    "allstate_claims_severity": "insurance",
    "santander_customer_transaction": "sentiment analysis",
    "otto_group_product": "retail",
    "bbcnews": "topic classification",
    "sst2": "sentiment analysis",
    "imdb_genre_prediction": "topic classification",
    "sst5": "sentiment analysis",
    "product_sentiment_machine_hack": "sentiment anlysis",
    "bookprice_prediction": "retail",
    "goemotions": "sentiment analysis",
    "jc_penney_products": "retail",
    "fake_job_postings2": "fraud detection",
    "data_scientist_salary": "human resources",
    "news_popularity2": "media",
    "women_clothing_review": "sentiment analysis",
    "ae_price_prediction": "retail",
    "news_channel": "media",
    "ieee_fraud": "fraud detection",
    "higgs": "scientific",
    "titanic": "insurance",
    "ohsumed_7400": "medical",
    "reuters_r8": "media",
    "jigsaw_unintended_bias100K": "sentiment analysis",
    "mercari_price_suggestion100K": "retail",
    "melbourne_airbnb": "real estate",
    "yelp_review_polarity": "sentiment analysis",
    "yelp_reviews": "sentiment analysis",
    "amazon_review_polarity": "sentiment analysis",
    "amazon_reviews": "sentiment analysis",
    "agnews": "media",
    "california_house_price": "real estate",
    "ethos_binary": "sentiment analysis",
    "wine_reviews": "sentiment analysis",
    "yahoo_answers": "sentiment analysis",
    "google_qa_answer_type_reason_explanation": "topic classification",
    "google_qa_question_type_reason_explanation": "topic classification",
    "bnp_claims_management": "insurance",
    "creditcard_fraud": "fraud detection",
    "imbalanced_insurance": "insurance",
    "walmart_recruiting": "retail",
}

all_datasets_tabular = [
    "ames_housing",
    "naval",
    "forest_cover",
    "santander_customer_satisfaction",
    "adult_census_income",
    "sarcos",
    "amazon_employee_access_challenge",
    "numerai28pt6",
    "mercedes_benz_greener",
    "mushroom_edibility",
    "connect4",
    "allstate_claims_severity",
    "santander_customer_transaction",
    "otto_group_product",
    "protein",
    "ieee_fraud",
    "higgs",
    "titanic",
    "bnp_claims_management",
    "creditcard_fraud",
    "imbalanced_insurance",
    "walmart_recruiting",
]

all_datasets_text = [
    "sst2",
    "sst5",
    "bookprice_prediction",
    "fake_job_postings2",
    "jc_penney_products",
    "goemotions",
    "product_sentiment_machine_hack",
    "imdb_genre_prediction",
    "bbcnews",
    "jigsaw_unintended_bias100K",
    "mercari_price_suggestion100K",
    "melbourne_airbnb",
    "yelp_review_polarity",
    "yelp_reviews",
    "amazon_review_polarity",
    "amazon_reviews",
    "agnews",
    "california_house_price",
    "ethos_binary",
    "wine_reviews",
    "yahoo_answers",
    "reuters_r8",
    "ohsumed_7400",
    "google_qa_answer_type_reason_explanation",
    "google_qa_question_type_reason_explanation",
    "ae_price_prediction",
    "data_scientist_salary",
    "news_channel",
    "news_popularity2",
]

AMES_HOUSING_CONFIG = """
output_features:
  - name: SalePrice
    type: number
input_features:
  - name: MSSubClass
    type: category
  - name: MSZoning
    type: category
  - name: LotFrontage
    type: number
  - name: LotArea
    type: number
  - name: Street
    type: category
  - name: Alley
    type: category
  - name: LotShape
    type: category
  - name: LandContour
    type: category
  - name: Utilities
    type: category
  - name: LotConfig
    type: category
  - name: LandSlope
    type: category
  - name: Neighborhood
    type: category
  - name: Condition1
    type: category
  - name: Condition2
    type: category
  - name: BldgType
    type: category
  - name: HouseStyle
    type: category
  - name: OverallQual
    type: category
  - name: OverallCond
    type: category
  - name: YearBuilt
    type: number
  - name: YearRemodAdd
    type: number
  - name: RoofStyle
    type: category
  - name: RoofMatl
    type: category
  - name: Exterior1st
    type: category
  - name: Exterior2nd
    type: category
  - name: MasVnrType
    type: category
  - name: MasVnrArea
    type: number
  - name: ExterQual
    type: category
  - name: ExterCond
    type: category
  - name: Foundation
    type: category
  - name: BsmtQual
    type: category
  - name: BsmtCond
    type: category
  - name: BsmtExposure
    type: category
  - name: BsmtFinType1
    type: category
  - name: BsmtFinSF1
    type: number
  - name: BsmtFinType2
    type: category
  - name: BsmtFinSF2
    type: number
  - name: BsmtUnfSF
    type: number
  - name: TotalBsmtSF
    type: number
  - name: Heating
    type: category
  - name: HeatingQC
    type: category
  - name: CentralAir
    type: binary
  - name: Electrical
    type: category
  - name: 1stFlrSF
    type: number
  - name: 2ndFlrSF
    type: number
  - name: LowQualFinSF
    type: number
  - name: GrLivArea
    type: number
  - name: BsmtFullBath
    type: number
  - name: BsmtHalfBath
    type: number
  - name: FullBath
    type: number
  - name: HalfBath
    type: number
  - name: BedroomAbvGr
    type: number
  - name: KitchenAbvGr
    type: number
  - name: KitchenQual
    type: category
  - name: TotRmsAbvGrd
    type: number
  - name: Functional
    type: category
  - name: Fireplaces
    type: number
  - name: FireplaceQu
    type: category
  - name: GarageType
    type: category
  - name: GarageYrBlt
    type: number
  - name: GarageFinish
    type: category
  - name: GarageCars
    type: number
  - name: GarageArea
    type: number
  - name: GarageQual
    type: category
  - name: GarageCond
    type: category
  - name: PavedDrive
    type: category
  - name: WoodDeckSF
    type: number
  - name: OpenPorchSF
    type: number
  - name: EnclosedPorch
    type: number
  - name: 3SsnPorch
    type: number
  - name: ScreenPorch
    type: number
  - name: PoolArea
    type: number
  - name: PoolQC
    type: category
  - name: Fence
    type: category
  - name: MiscFeature
    type: category
  - name: MiscVal
    type: number
  - name: MoSold
    type: category
  - name: YrSold
    type: number
  - name: SaleType
    type: category
  - name: SaleCondition
    type: category
"""
MERCEDES_BENZ_GREENER_CONFIG = """
output_features:
  - name: y
    type: number
input_features:
  - name: X0
    type: category
  - name: X1
    type: category
  - name: X2
    type: category
  - name: X3
    type: category
  - name: X4
    type: category
  - name: X5
    type: category
  - name: X6
    type: category
  - name: X8
    type: category
  - name: X10
    type: binary
  - name: X11
    type: binary
  - name: X12
    type: binary
  - name: X13
    type: binary
  - name: X14
    type: binary
  - name: X15
    type: binary
  - name: X16
    type: binary
  - name: X17
    type: binary
  - name: X18
    type: binary
  - name: X19
    type: binary
  - name: X20
    type: binary
  - name: X21
    type: binary
  - name: X22
    type: binary
  - name: X23
    type: binary
  - name: X24
    type: binary
  - name: X26
    type: binary
  - name: X27
    type: binary
  - name: X28
    type: binary
  - name: X29
    type: binary
  - name: X30
    type: binary
  - name: X31
    type: binary
  - name: X32
    type: binary
  - name: X33
    type: binary
  - name: X34
    type: binary
  - name: X35
    type: binary
  - name: X36
    type: binary
  - name: X37
    type: binary
  - name: X38
    type: binary
  - name: X39
    type: binary
  - name: X40
    type: binary
  - name: X41
    type: binary
  - name: X42
    type: binary
  - name: X43
    type: binary
  - name: X44
    type: binary
  - name: X45
    type: binary
  - name: X46
    type: binary
  - name: X47
    type: binary
  - name: X48
    type: binary
  - name: X49
    type: binary
  - name: X50
    type: binary
  - name: X51
    type: binary
  - name: X52
    type: binary
  - name: X53
    type: binary
  - name: X54
    type: binary
  - name: X55
    type: binary
  - name: X56
    type: binary
  - name: X57
    type: binary
  - name: X58
    type: binary
  - name: X59
    type: binary
  - name: X60
    type: binary
  - name: X61
    type: binary
  - name: X62
    type: binary
  - name: X63
    type: binary
  - name: X64
    type: binary
  - name: X65
    type: binary
  - name: X66
    type: binary
  - name: X67
    type: binary
  - name: X68
    type: binary
  - name: X69
    type: binary
  - name: X70
    type: binary
  - name: X71
    type: binary
  - name: X73
    type: binary
  - name: X74
    type: binary
  - name: X75
    type: binary
  - name: X76
    type: binary
  - name: X77
    type: binary
  - name: X78
    type: binary
  - name: X79
    type: binary
  - name: X80
    type: binary
  - name: X81
    type: binary
  - name: X82
    type: binary
  - name: X83
    type: binary
  - name: X84
    type: binary
  - name: X85
    type: binary
  - name: X86
    type: binary
  - name: X87
    type: binary
  - name: X88
    type: binary
  - name: X89
    type: binary
  - name: X90
    type: binary
  - name: X91
    type: binary
  - name: X92
    type: binary
  - name: X93
    type: binary
  - name: X94
    type: binary
  - name: X95
    type: binary
  - name: X96
    type: binary
  - name: X97
    type: binary
  - name: X98
    type: binary
  - name: X99
    type: binary
  - name: X100
    type: binary
  - name: X101
    type: binary
  - name: X102
    type: binary
  - name: X103
    type: binary
  - name: X104
    type: binary
  - name: X105
    type: binary
  - name: X106
    type: binary
  - name: X107
    type: binary
  - name: X108
    type: binary
  - name: X109
    type: binary
  - name: X110
    type: binary
  - name: X111
    type: binary
  - name: X112
    type: binary
  - name: X113
    type: binary
  - name: X114
    type: binary
  - name: X115
    type: binary
  - name: X116
    type: binary
  - name: X117
    type: binary
  - name: X118
    type: binary
  - name: X119
    type: binary
  - name: X120
    type: binary
  - name: X122
    type: binary
  - name: X123
    type: binary
  - name: X124
    type: binary
  - name: X125
    type: binary
  - name: X126
    type: binary
  - name: X127
    type: binary
  - name: X128
    type: binary
  - name: X129
    type: binary
  - name: X130
    type: binary
  - name: X131
    type: binary
  - name: X132
    type: binary
  - name: X133
    type: binary
  - name: X134
    type: binary
  - name: X135
    type: binary
  - name: X136
    type: binary
  - name: X137
    type: binary
  - name: X138
    type: binary
  - name: X139
    type: binary
  - name: X140
    type: binary
  - name: X141
    type: binary
  - name: X142
    type: binary
  - name: X143
    type: binary
  - name: X144
    type: binary
  - name: X145
    type: binary
  - name: X146
    type: binary
  - name: X147
    type: binary
  - name: X148
    type: binary
  - name: X150
    type: binary
  - name: X151
    type: binary
  - name: X152
    type: binary
  - name: X153
    type: binary
  - name: X154
    type: binary
  - name: X155
    type: binary
  - name: X156
    type: binary
  - name: X157
    type: binary
  - name: X158
    type: binary
  - name: X159
    type: binary
  - name: X160
    type: binary
  - name: X161
    type: binary
  - name: X162
    type: binary
  - name: X163
    type: binary
  - name: X164
    type: binary
  - name: X165
    type: binary
  - name: X166
    type: binary
  - name: X167
    type: binary
  - name: X168
    type: binary
  - name: X169
    type: binary
  - name: X170
    type: binary
  - name: X171
    type: binary
  - name: X172
    type: binary
  - name: X173
    type: binary
  - name: X174
    type: binary
  - name: X175
    type: binary
  - name: X176
    type: binary
  - name: X177
    type: binary
  - name: X178
    type: binary
  - name: X179
    type: binary
  - name: X180
    type: binary
  - name: X181
    type: binary
  - name: X182
    type: binary
  - name: X183
    type: binary
  - name: X184
    type: binary
  - name: X185
    type: binary
  - name: X186
    type: binary
  - name: X187
    type: binary
  - name: X189
    type: binary
  - name: X190
    type: binary
  - name: X191
    type: binary
  - name: X192
    type: binary
  - name: X194
    type: binary
  - name: X195
    type: binary
  - name: X196
    type: binary
  - name: X197
    type: binary
  - name: X198
    type: binary
  - name: X199
    type: binary
  - name: X200
    type: binary
  - name: X201
    type: binary
  - name: X202
    type: binary
  - name: X203
    type: binary
  - name: X204
    type: binary
  - name: X205
    type: binary
  - name: X206
    type: binary
  - name: X207
    type: binary
  - name: X208
    type: binary
  - name: X209
    type: binary
  - name: X210
    type: binary
  - name: X211
    type: binary
  - name: X212
    type: binary
  - name: X213
    type: binary
  - name: X214
    type: binary
  - name: X215
    type: binary
  - name: X216
    type: binary
  - name: X217
    type: binary
  - name: X218
    type: binary
  - name: X219
    type: binary
  - name: X220
    type: binary
  - name: X221
    type: binary
  - name: X222
    type: binary
  - name: X223
    type: binary
  - name: X224
    type: binary
  - name: X225
    type: binary
  - name: X226
    type: binary
  - name: X227
    type: binary
  - name: X228
    type: binary
  - name: X229
    type: binary
  - name: X230
    type: binary
  - name: X231
    type: binary
  - name: X232
    type: binary
  - name: X233
    type: binary
  - name: X234
    type: binary
  - name: X235
    type: binary
  - name: X236
    type: binary
  - name: X237
    type: binary
  - name: X238
    type: binary
  - name: X239
    type: binary
  - name: X240
    type: binary
  - name: X241
    type: binary
  - name: X242
    type: binary
  - name: X243
    type: binary
  - name: X244
    type: binary
  - name: X245
    type: binary
  - name: X246
    type: binary
  - name: X247
    type: binary
  - name: X248
    type: binary
  - name: X249
    type: binary
  - name: X250
    type: binary
  - name: X251
    type: binary
  - name: X252
    type: binary
  - name: X253
    type: binary
  - name: X254
    type: binary
  - name: X255
    type: binary
  - name: X256
    type: binary
  - name: X257
    type: binary
  - name: X258
    type: binary
  - name: X259
    type: binary
  - name: X260
    type: binary
  - name: X261
    type: binary
  - name: X262
    type: binary
  - name: X263
    type: binary
  - name: X264
    type: binary
  - name: X265
    type: binary
  - name: X266
    type: binary
  - name: X267
    type: binary
  - name: X268
    type: binary
  - name: X269
    type: binary
  - name: X270
    type: binary
  - name: X271
    type: binary
  - name: X272
    type: binary
  - name: X273
    type: binary
  - name: X274
    type: binary
  - name: X275
    type: binary
  - name: X276
    type: binary
  - name: X277
    type: binary
  - name: X278
    type: binary
  - name: X279
    type: binary
  - name: X280
    type: binary
  - name: X281
    type: binary
  - name: X282
    type: binary
  - name: X283
    type: binary
  - name: X284
    type: binary
  - name: X285
    type: binary
  - name: X286
    type: binary
  - name: X287
    type: binary
  - name: X288
    type: binary
  - name: X289
    type: binary
  - name: X290
    type: binary
  - name: X291
    type: binary
  - name: X292
    type: binary
  - name: X293
    type: binary
  - name: X294
    type: binary
  - name: X295
    type: binary
  - name: X296
    type: binary
  - name: X297
    type: binary
  - name: X298
    type: binary
  - name: X299
    type: binary
  - name: X300
    type: binary
  - name: X301
    type: binary
  - name: X302
    type: binary
  - name: X304
    type: binary
  - name: X305
    type: binary
  - name: X306
    type: binary
  - name: X307
    type: binary
  - name: X308
    type: binary
  - name: X309
    type: binary
  - name: X310
    type: binary
  - name: X311
    type: binary
  - name: X312
    type: binary
  - name: X313
    type: binary
  - name: X314
    type: binary
  - name: X315
    type: binary
  - name: X316
    type: binary
  - name: X317
    type: binary
  - name: X318
    type: binary
  - name: X319
    type: binary
  - name: X320
    type: binary
  - name: X321
    type: binary
  - name: X322
    type: binary
  - name: X323
    type: binary
  - name: X324
    type: binary
  - name: X325
    type: binary
  - name: X326
    type: binary
  - name: X327
    type: binary
  - name: X328
    type: binary
  - name: X329
    type: binary
  - name: X330
    type: binary
  - name: X331
    type: binary
  - name: X332
    type: binary
  - name: X333
    type: binary
  - name: X334
    type: binary
  - name: X335
    type: binary
  - name: X336
    type: binary
  - name: X337
    type: binary
  - name: X338
    type: binary
  - name: X339
    type: binary
  - name: X340
    type: binary
  - name: X341
    type: binary
  - name: X342
    type: binary
  - name: X343
    type: binary
  - name: X344
    type: binary
  - name: X345
    type: binary
  - name: X346
    type: binary
  - name: X347
    type: binary
  - name: X348
    type: binary
  - name: X349
    type: binary
  - name: X350
    type: binary
  - name: X351
    type: binary
  - name: X352
    type: binary
  - name: X353
    type: binary
  - name: X354
    type: binary
  - name: X355
    type: binary
  - name: X356
    type: binary
  - name: X357
    type: binary
  - name: X358
    type: binary
  - name: X359
    type: binary
  - name: X360
    type: binary
  - name: X361
    type: binary
  - name: X362
    type: binary
  - name: X363
    type: binary
  - name: X364
    type: binary
  - name: X365
    type: binary
  - name: X366
    type: binary
  - name: X367
    type: binary
  - name: X368
    type: binary
  - name: X369
    type: binary
  - name: X370
    type: binary
  - name: X371
    type: binary
  - name: X372
    type: binary
  - name: X373
    type: binary
  - name: X374
    type: binary
  - name: X375
    type: binary
  - name: X376
    type: binary
  - name: X377
    type: binary
  - name: X378
    type: binary
  - name: X379
    type: binary
  - name: X380
    type: binary
  - name: X382
    type: binary
  - name: X383
    type: binary
  - name: X384
    type: binary
  - name: X385
    type: binary
"""
BBCNEWS_CONFIG = """
output_features:
  - name: Category
    type: category
input_features:
  - name: Text
    type: text
"""

PRODUCT_SENTIMENT_MACHINE_HACK_NO_TEXT = """
input_features:
  - name: Product_Type
    type: category
    column: Product_Type
output_features:
  - name: Sentiment
    type: category
    column: Sentiment
"""

ADULT_CENSUS_INCOME = """
input_features:
  - name: age
    type: number
  - name: workclass
    type: category
  - name: fnlwgt
    type: number
  - name: education
    type: category
  - name: education-num
    type: number
  - name: marital-status
    type: category
  - name: occupation
    type: category
  - name: relationship
    type: category
  - name: race
    type: category
  - name: sex
    type: category
  - name: capital-gain
    type: number
  - name: capital-loss
    type: number
  - name: hours-per-week
    type: number
  - name: native-country
    type: category
output_features:
  - name: income
    type: binary
"""

FAKE_JOB_POSTINGS_MULTI_TO_TEXT = """
input_features:
  - name: description
    type: text
    column: description
  - name: required_experience
    type: category
    column: required_experience
  - name: required_education
    type: category
    column: required_education
output_features:
  - name: title
    type: text
    column: title
"""

TITANIC = """
input_features:
  - name: Pclass
    type: category
    column: Pclass
  - name: Sex
    type: category
    column: Sex
  - name: Age
    type: number
    column: Age
  - name: SibSp
    type: number
    column: SibSp
  - name: Parch
    type: number
    column: Parch
  - name: Fare
    type: number
    column: Fare
  - name: Embarked
    type: category
    column: Embarked
output_features:
  - name: Survived
    type: category
    column: Survived
"""

feature_type_to_config_for_encoder_preprocessing = {
    "number": (AMES_HOUSING_CONFIG, "ames_housing"),
    "category": (AMES_HOUSING_CONFIG, "ames_housing"),
    "binary": (MERCEDES_BENZ_GREENER_CONFIG, "mercedes_benz_greener"),
    "text": (BBCNEWS_CONFIG, "bbcnews"),
}


feature_type_to_config_for_decoder_loss = {
    "number": (AMES_HOUSING_CONFIG, "ames_housing"),
    "category": (PRODUCT_SENTIMENT_MACHINE_HACK_NO_TEXT, "product_sentiment_machine_hack"),
    "binary": (ADULT_CENSUS_INCOME, "adult_census_income"),
    "text": (FAKE_JOB_POSTINGS_MULTI_TO_TEXT, "fake_job_postings2"),
}
