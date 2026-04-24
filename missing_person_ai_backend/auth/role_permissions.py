ROLE_PERMISSIONS = {
    1: ["create_case"],  # citizen

    2: [   # police
        "view_case",
        "update_case",
        "create_fir",
        "cctv_access",
        "ai_recognition",
        "alerts"
    ],

    3: ["all"]  # admin
}
