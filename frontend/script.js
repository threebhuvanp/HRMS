/* =========================================================
   WORKFORCEAI
   UNIFIED JAVASCRIPT

   LOGIN
   GOOGLE LOGIN
   DASHBOARD
   PERFORMANCE INTELLIGENCE
   WORKFORCE RISK
   AI INSIGHTS
========================================================= */


/* =========================================================
   GLOBAL DATA
========================================================= */

let allEmployees = [];
let intelligenceData = [];


/* =========================================================
   GOOGLE CONFIGURATION
========================================================= */

const GOOGLE_CLIENT_ID =
    "188759653861-r7u2q8g5nt0v6g2ge2lgttjscm1t11as.apps.googleusercontent.com";


/* =========================================================
   PAGE INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializePage();

    }
);


/* =========================================================
   DETECT CURRENT PAGE
========================================================= */

function initializePage() {

    const loginForm =
        document.querySelector("#loginForm");

    const dashboardTable =
        document.querySelector("#employeeTableBody");


    if (loginForm) {

        initializeLogin();

    }


    if (dashboardTable) {

        loadDashboard();

    }

}


/* =========================================================
   LOGIN INITIALIZATION
========================================================= */

function initializeLogin() {

    const loginForm =
        document.querySelector("#loginForm");


    if (!loginForm) {

        return;

    }


    loginForm.addEventListener(
        "submit",
        handleLogin
    );


    initializeForgotPassword();

    initializeGoogleLogin();

}


/* =========================================================
   PASSWORD LOGIN
========================================================= */

async function handleLogin(event) {

    event.preventDefault();


    const emailInput =
        document.querySelector("#email") ||
        document.querySelector("#workEmail") ||
        document.querySelector('input[type="email"]');


    const passwordInput =
        document.querySelector("#password") ||
        document.querySelector("#workPassword") ||
        document.querySelector('input[type="password"]');


    if (!emailInput || !passwordInput) {

        alert(
            "Email or password field not found."
        );

        return;

    }


    const email =
        emailInput.value.trim();

    const password =
        passwordInput.value;


    if (!email || !password) {

        alert(
            "Please enter your email and password."
        );

        return;

    }


    const loginButton =
        loginFormButton();


    if (loginButton) {

        loginButton.disabled = true;

        loginButton.dataset.originalText =
            loginButton.innerText;

        loginButton.innerText =
            "Signing in...";

    }


    try {

        const response =
            await fetch(
                "/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    credentials:
                        "same-origin",

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );


        const data =
            await response.json();


        if (response.ok) {

            window.location.href =
                "/dashboard";

            return;

        }


        alert(
            data.error ||
            "Login failed. Please check your credentials."
        );


    } catch (error) {

        console.error(
            "Login error:",
            error
        );


        alert(
            "Unable to connect to WorkforceAI backend."
        );

    } finally {

        if (loginButton) {

            loginButton.disabled = false;

            loginButton.innerText =
                loginButton.dataset.originalText ||
                "Sign in to WorkforceAI";

        }

    }

}


/* =========================================================
   FIND LOGIN BUTTON
========================================================= */

function loginFormButton() {

    return (
        document.querySelector(
            "#loginForm button[type='submit']"
        ) ||
        document.querySelector(
            ".login-btn"
        ) ||
        document.querySelector(
            "button[type='submit']"
        )
    );

}


/* =========================================================
   GOOGLE LOGIN INITIALIZATION
========================================================= */

function initializeGoogleLogin() {

    const googleContainer =
        document.getElementById(
            "googleButton"
        );


    if (!googleContainer) {

        return;

    }


    if (
        window.google &&
        window.google.accounts &&
        window.google.accounts.id
    ) {

        renderGoogleButton();

        return;

    }


    let attempts = 0;

    const maxAttempts = 50;


    const waitForGoogle =
        setInterval(
            () => {

                attempts++;


                if (
                    window.google &&
                    window.google.accounts &&
                    window.google.accounts.id
                ) {

                    clearInterval(
                        waitForGoogle
                    );

                    renderGoogleButton();

                }


                if (
                    attempts >= maxAttempts
                ) {

                    clearInterval(
                        waitForGoogle
                    );

                    showGoogleStatus(
                        "Google Login could not load. Check your internet connection."
                    );

                }

            },
            200
        );

}


/* =========================================================
   RENDER GOOGLE BUTTON
========================================================= */

function renderGoogleButton() {

    const googleContainer =
        document.getElementById(
            "googleButton"
        );


    if (!googleContainer) {

        return;

    }


    googleContainer.innerHTML = "";


    try {

        google.accounts.id.initialize({

            client_id:
                GOOGLE_CLIENT_ID,

            callback:
                handleGoogleCredential,

            ux_mode:
                "popup"

        });


        const availableWidth =
            googleContainer.clientWidth;


        const buttonWidth =
            Math.min(
                400,
                Math.max(
                    200,
                    Math.floor(
                        availableWidth
                    )
                )
            );


        google.accounts.id.renderButton(
            googleContainer,
            {
                type: "standard",

                theme: "outline",

                size: "large",

                text: "continue_with",

                shape: "rectangular",

                logo_alignment: "left",

                width: buttonWidth,

                locale: "en"
            }
        );


    } catch (error) {

        console.error(
            "Google button error:",
            error
        );


        showGoogleStatus(
            "Google Login could not be initialized."
        );

    }

}


/* =========================================================
   GOOGLE CREDENTIAL CALLBACK
========================================================= */

async function handleGoogleCredential(
    response
) {

    if (
        !response ||
        !response.credential
    ) {

        showGoogleStatus(
            "Google did not return a valid credential."
        );

        return;

    }


    setGoogleLoading(true);

    clearGoogleStatus();


    try {

        const backendResponse =
            await fetch(
                "/google-login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    credentials:
                        "same-origin",

                    body: JSON.stringify({

                        credential:
                            response.credential

                    })

                }
            );


        const data =
            await backendResponse.json();


        if (
            backendResponse.ok
        ) {

            window.location.href =
                "/dashboard";

            return;

        }


        showGoogleStatus(
            data.error ||
            "Google login failed."
        );


    } catch (error) {

        console.error(
            "Google login error:",
            error
        );


        showGoogleStatus(
            "Unable to connect to WorkforceAI backend."
        );

    } finally {

        setGoogleLoading(false);

    }

}


/* =========================================================
   GOOGLE LOADING
========================================================= */

function setGoogleLoading(
    loading
) {

    const container =
        document.getElementById(
            "googleButton"
        );


    if (!container) {

        return;

    }


    if (loading) {

        container.classList.add(
            "loading"
        );

    } else {

        container.classList.remove(
            "loading"
        );

    }

}


/* =========================================================
   GOOGLE STATUS
========================================================= */

function showGoogleStatus(
    message
) {

    const status =
        document.getElementById(
            "googleStatus"
        );


    if (!status) {

        return;

    }


    status.textContent =
        message;

}


function clearGoogleStatus() {

    const status =
        document.getElementById(
            "googleStatus"
        );


    if (!status) {

        return;

    }


    status.textContent =
        "";

}


/* =========================================================
   FORGOT PASSWORD
========================================================= */

function initializeForgotPassword() {

    const button =
        document.getElementById(
            "forgotPasswordButton"
        );


    if (!button) {

        return;

    }


    button.addEventListener(
        "click",
        () => {

            alert(
                "Password recovery will be connected to secure email OTP in the next authentication phase."
            );

        }
    );

}


/* =========================================================
   LOAD COMPLETE DASHBOARD
========================================================= */

async function loadDashboard() {

    try {

        await loadCurrentUser();

        await loadEmployees();

        await loadPerformanceIntelligence();

    } catch (error) {

        console.error(
            "Dashboard loading error:",
            error
        );

    }

}


/* =========================================================
   LOAD CURRENT USER
========================================================= */

async function loadCurrentUser() {

    const response =
        await fetch(
            "/me",
            {
                method: "GET",

                credentials:
                    "same-origin"
            }
        );


    if (!response.ok) {

        if (
            response.status === 401
        ) {

            window.location.href =
                "/app";

        }

        return;

    }


    const data =
        await response.json();


    if (!data.user) {

        return;

    }


    const user =
        data.user;


    const nameElement =
        document.getElementById(
            "userName"
        );


    const roleElement =
        document.getElementById(
            "userRole"
        );


    const avatarElement =
        document.getElementById(
            "userAvatar"
        );


    if (nameElement) {

        nameElement.textContent =
            user.name;

    }


    if (roleElement) {

        roleElement.textContent =
            formatRole(
                user.role
            );

    }


    if (avatarElement) {

        avatarElement.textContent =
            getInitials(
                user.name
            );

    }

}


/* =========================================================
   FORMAT ROLE
========================================================= */

function formatRole(role) {

    if (!role) {

        return "Workforce User";

    }


    const roleMap = {

        hr:
            "Human Resources",

        admin:
            "Administrator",

        manager:
            "Manager",

        employee:
            "Employee"

    };


    return (
        roleMap[role] ||
        role.charAt(0).toUpperCase() +
        role.slice(1)
    );

}


/* =========================================================
   LOAD EMPLOYEES
========================================================= */

async function loadEmployees() {

    const response =
        await fetch(
            "/employees",
            {
                method: "GET",

                credentials:
                    "same-origin"
            }
        );


    if (!response.ok) {

        if (
            response.status === 401 ||
            response.status === 403
        ) {

            window.location.href =
                "/app";

        }


        throw new Error(
            "Could not load employees"
        );

    }


    const data =
        await response.json();


    allEmployees =
        data.employees || [];


    updateStatistics(
        allEmployees
    );


    renderDepartmentChart(
        allEmployees
    );


    renderEmployeeTable(
        allEmployees
    );

}


/* =========================================================
   PERFORMANCE INTELLIGENCE
========================================================= */

async function loadPerformanceIntelligence() {

    const response =
        await fetch(
            "/intelligence/performance",
            {
                method: "GET",

                credentials:
                    "same-origin"
            }
        );


    if (!response.ok) {

        console.error(
            "Performance intelligence request failed:",
            response.status
        );

        return;

    }


    const data =
        await response.json();


    intelligenceData =
        data.results || [];


    updateIntelligenceStatistics(
        intelligenceData
    );


    renderIntelligencePanel(
        intelligenceData
    );

}


/* =========================================================
   UPDATE BASIC STATISTICS
========================================================= */

function updateStatistics(
    employees
) {

    const total =
        employees.length;


    const active =
        employees.filter(
            employee =>
                employee.status === "active"
        ).length;


    const departmentSet =
        new Set();


    employees.forEach(
        employee => {

            if (
                employee.department
            ) {

                departmentSet.add(
                    employee.department
                );

            }

        }
    );


    const totalDepartments =
        departmentSet.size;


    setElementText(
        "totalEmployees",
        total
    );


    setElementText(
        "activeEmployees",
        active
    );


    setElementText(
        "totalDepartments",
        totalDepartments
    );

}


/* =========================================================
   UPDATE INTELLIGENCE STATISTICS
========================================================= */

function updateIntelligenceStatistics(
    results
) {

    if (!results.length) {

        setElementText(
            "riskEmployees",
            "0"
        );

        return;

    }


    const highRisk =
        results.filter(
            item =>
                item.risk_level === "High"
        ).length;


    const mediumRisk =
        results.filter(
            item =>
                item.risk_level === "Medium"
        ).length;


    setElementText(
        "riskEmployees",
        highRisk + mediumRisk
    );


    const performanceValues =
        results
            .map(
                item =>
                    Number(
                        item.current_performance
                    )
            )
            .filter(
                value =>
                    !Number.isNaN(value)
            );


    const averagePerformance =
        performanceValues.length
            ? performanceValues.reduce(
                (sum, value) =>
                    sum + value,
                0
            ) /
            performanceValues.length
            : 0;


    /* Optional KPI if your HTML contains it */

    const averageElement =
        document.getElementById(
            "averagePerformance"
        );


    if (averageElement) {

        averageElement.textContent =
            `${averagePerformance.toFixed(1)}%`;

    }


    /* Optional KPI */

    const highRiskElement =
        document.getElementById(
            "highRiskEmployees"
        );


    if (highRiskElement) {

        highRiskElement.textContent =
            highRisk;

    }


    /* Optional KPI */

    const mediumRiskElement =
        document.getElementById(
            "mediumRiskEmployees"
        );


    if (mediumRiskElement) {

        mediumRiskElement.textContent =
            mediumRisk;

    }

}


/* =========================================================
   AI INTELLIGENCE PANEL
========================================================= */

function renderIntelligencePanel(
    results
) {

    let panel =
        document.getElementById(
            "workforceIntelligencePanel"
        );


    /*
       If the HTML doesn't already contain
       our intelligence panel, create it.
    */

    if (!panel) {

        panel =
            document.createElement(
                "section"
            );

        panel.id =
            "workforceIntelligencePanel";

        panel.className =
            "glass-card";

        const main =
            document.querySelector(
                ".dashboard-main"
            );


        if (!main) {

            return;

        }


        const statsGrid =
            document.querySelector(
                ".stats-grid"
            );


        if (statsGrid) {

            statsGrid.insertAdjacentElement(
                "afterend",
                panel
            );

        } else {

            main.appendChild(
                panel
            );

        }

    }


    if (!results.length) {

        panel.innerHTML = `

            <div style="
                padding: 30px;
                text-align: center;
            ">

                <div style="
                    font-size: 32px;
                    margin-bottom: 10px;
                ">
                    ✦
                </div>

                <h2>
                    Workforce Intelligence
                </h2>

                <p>
                    No performance intelligence
                    is available yet.
                </p>

            </div>

        `;

        return;

    }


    const highRisk =
        results.filter(
            item =>
                item.risk_level === "High"
        );


    const mediumRisk =
        results.filter(
            item =>
                item.risk_level === "Medium"
        );


    const lowRisk =
        results.filter(
            item =>
                item.risk_level === "Low"
        );


    const averagePerformance =
        results.reduce(
            (sum, item) =>
                sum +
                Number(
                    item.current_performance || 0
                ),
            0
        ) /
        results.length;


    const averageGoal =
        results.reduce(
            (sum, item) =>
                sum +
                Number(
                    item.goal_completion || 0
                ),
            0
        ) /
        results.length;


    const averageAttendance =
        results.reduce(
            (sum, item) =>
                sum +
                Number(
                    item.attendance_rate || 0
                ),
            0
        ) /
        results.length;


    const sortedResults =
        [...results].sort(
            (a, b) =>
                Number(b.risk_score) -
                Number(a.risk_score)
        );


    const topRiskEmployees =
        sortedResults.slice(
            0,
            Math.min(5, sortedResults.length)
        );


    panel.innerHTML = `

        <div style="
            padding: 28px;
        ">

            <!-- HEADER -->

            <div style="
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 20px;
                margin-bottom: 24px;
                flex-wrap: wrap;
            ">

                <div>

                    <div style="
                        font-size: 12px;
                        font-weight: 700;
                        letter-spacing: 1.5px;
                        opacity: 0.65;
                        margin-bottom: 7px;
                    ">
                        ✦ WORKFORCEAI INTELLIGENCE ENGINE
                    </div>

                    <h2 style="
                        margin: 0 0 8px 0;
                        font-size: 25px;
                    ">
                        What is happening in your workforce?
                    </h2>

                    <p style="
                        margin: 0;
                        opacity: 0.65;
                    ">
                        Performance, goals and attendance
                        analyzed together.
                    </p>

                </div>


                <div style="
                    padding: 8px 13px;
                    border-radius: 20px;
                    background: rgba(22, 163, 74, 0.10);
                    font-size: 12px;
                    font-weight: 700;
                ">

                    ● LIVE ANALYSIS

                </div>

            </div>


            <!-- SUMMARY -->

            <div style="
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(160px, 1fr));
                gap: 14px;
                margin-bottom: 28px;
            ">

                ${intelligenceMetric(
                    "Average Performance",
                    `${averagePerformance.toFixed(1)}%`,
                    "Overall workforce performance"
                )}

                ${intelligenceMetric(
                    "Goal Completion",
                    `${averageGoal.toFixed(1)}%`,
                    "Average employee progress"
                )}

                ${intelligenceMetric(
                    "Attendance",
                    `${averageAttendance.toFixed(1)}%`,
                    "Workforce attendance rate"
                )}

                ${intelligenceMetric(
                    "Risk Signals",
                    `${highRisk.length + mediumRisk.length}`,
                    "Employees needing attention"
                )}

            </div>


            <!-- DECISION SUMMARY -->

            <div style="
                padding: 20px;
                border-radius: 18px;
                background:
                    linear-gradient(
                        135deg,
                        rgba(22, 163, 74, 0.08),
                        rgba(255,255,255,0.55)
                    );
                border: 1px solid rgba(22, 163, 74, 0.12);
                margin-bottom: 26px;
            ">

                <div style="
                    font-size: 12px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    margin-bottom: 10px;
                ">
                    AI DECISION SUMMARY
                </div>

                <div style="
                    font-size: 17px;
                    font-weight: 700;
                    margin-bottom: 7px;
                ">

                    ${
                        highRisk.length
                        ? `${highRisk.length} employee${highRisk.length > 1 ? "s" : ""} show high-risk signals.`
                        : "No employees currently show high-risk signals."
                    }

                </div>

                <div style="
                    font-size: 14px;
                    opacity: 0.7;
                    line-height: 1.6;
                ">

                    ${
                        mediumRisk.length
                        ? `${mediumRisk.length} additional employee${mediumRisk.length > 1 ? "s" : ""} may benefit from closer monitoring.`
                        : "The current workforce shows relatively stable risk indicators."
                    }

                </div>

            </div>


            <!-- RISK EMPLOYEES -->

            <div style="
                margin-bottom: 12px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 1px;
                opacity: 0.65;
            ">
                EMPLOYEE INTELLIGENCE
            </div>


            <div style="
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(290px, 1fr));
                gap: 16px;
            ">

                ${
                    topRiskEmployees
                    .map(
                        item =>
                            intelligenceEmployeeCard(
                                item
                            )
                    )
                    .join("")
                }

            </div>


            <!-- LEGEND -->

            <div style="
                display: flex;
                gap: 18px;
                flex-wrap: wrap;
                margin-top: 22px;
                font-size: 12px;
                opacity: 0.65;
            ">

                <span>● High Risk</span>

                <span>● Medium Risk</span>

                <span>● Low Risk</span>

            </div>

        </div>

    `;

}


/* =========================================================
   INTELLIGENCE METRIC
========================================================= */

function intelligenceMetric(
    title,
    value,
    subtitle
) {

    return `

        <div style="
            padding: 18px;
            border-radius: 16px;
            background: rgba(255,255,255,0.55);
            border: 1px solid rgba(0,0,0,0.05);
        ">

            <div style="
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.7px;
                opacity: 0.55;
                margin-bottom: 9px;
            ">
                ${title}
            </div>

            <div style="
                font-size: 26px;
                font-weight: 800;
                margin-bottom: 5px;
            ">
                ${value}
            </div>

            <div style="
                font-size: 11px;
                opacity: 0.55;
            ">
                ${subtitle}
            </div>

        </div>

    `;

}


/* =========================================================
   EMPLOYEE INTELLIGENCE CARD
========================================================= */

function intelligenceEmployeeCard(
    item
) {

    const risk =
        item.risk_level || "Low";


    const riskScore =
        Number(
            item.risk_score || 0
        );


    const performance =
        Number(
            item.current_performance || 0
        );


    const trend =
        Number(
            item.performance_trend || 0
        );


    const trendSymbol =
        trend > 0
            ? "↑"
            : trend < 0
                ? "↓"
                : "→";


    const trendText =
        `${trendSymbol} ${Math.abs(trend).toFixed(1)}%`;


    const reasons =
        item.risk_reasons || [];


    const reasonsHTML =
        reasons.length
            ? reasons
                .slice(0, 3)
                .map(
                    reason =>
                        `<li>${escapeHTML(reason)}</li>`
                )
                .join("")
            : "<li>No major risk signal detected</li>";


    return `

        <div style="
            padding: 20px;
            border-radius: 18px;
            background: rgba(255,255,255,0.60);
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
        ">

            <!-- EMPLOYEE HEADER -->

            <div style="
                display: flex;
                justify-content: space-between;
                gap: 10px;
                margin-bottom: 18px;
            ">

                <div>

                    <div style="
                        font-weight: 800;
                        font-size: 17px;
                    ">
                        ${escapeHTML(
                            item.employee_code
                        )}
                    </div>

                    <div style="
                        font-size: 12px;
                        opacity: 0.6;
                        margin-top: 4px;
                    ">
                        ${escapeHTML(
                            item.designation || ""
                        )}
                        ·
                        ${escapeHTML(
                            item.department || ""
                        )}
                    </div>

                </div>


                <div style="
                    padding: 6px 10px;
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: 800;
                    background: rgba(0,0,0,0.05);
                ">

                    ${risk.toUpperCase()}

                </div>

            </div>


            <!-- METRICS -->

            <div style="
                display: grid;
                grid-template-columns:
                    repeat(3, 1fr);
                gap: 8px;
                margin-bottom: 17px;
            ">

                ${smallMetric(
                    "Performance",
                    `${performance.toFixed(1)}%`
                )}

                ${smallMetric(
                    "Trend",
                    trendText
                )}

                ${smallMetric(
                    "Risk",
                    `${riskScore}`
                )}

            </div>


            <!-- GOAL + ATTENDANCE -->

            <div style="
                display: grid;
                grid-template-columns:
                    1fr 1fr;
                gap: 12px;
                margin-bottom: 17px;
            ">

                <div>

                    <div style="
                        font-size: 11px;
                        opacity: 0.55;
                        margin-bottom: 5px;
                    ">
                        Goal completion
                    </div>

                    <strong>
                        ${Number(
                            item.goal_completion || 0
                        ).toFixed(1)}%
                    </strong>

                </div>


                <div>

                    <div style="
                        font-size: 11px;
                        opacity: 0.55;
                        margin-bottom: 5px;
                    ">
                        Attendance
                    </div>

                    <strong>
                        ${Number(
                            item.attendance_rate || 0
                        ).toFixed(1)}%
                    </strong>

                </div>

            </div>


            <!-- WHY -->

            <div style="
                padding: 13px;
                border-radius: 13px;
                background: rgba(0,0,0,0.025);
                margin-bottom: 13px;
            ">

                <div style="
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 0.8px;
                    opacity: 0.55;
                    margin-bottom: 7px;
                ">
                    WHY THIS SIGNAL APPEARED
                </div>

                <ul style="
                    margin: 0;
                    padding-left: 18px;
                    font-size: 12px;
                    line-height: 1.7;
                ">

                    ${reasonsHTML}

                </ul>

            </div>


            <!-- INSIGHT -->

            <div style="
                font-size: 13px;
                line-height: 1.6;
                margin-bottom: 12px;
            ">

                <strong>
                    ✦ Insight:
                </strong>

                ${escapeHTML(
                    item.insight || ""
                )}

            </div>


            <!-- RECOMMENDATION -->

            <div style="
                padding: 13px;
                border-radius: 13px;
                background: rgba(22, 163, 74, 0.07);
                font-size: 12px;
                line-height: 1.6;
            ">

                <strong>
                    → HR Recommendation
                </strong>

                <br>

                ${escapeHTML(
                    item.recommendation || ""
                )}

            </div>

        </div>

    `;

}


/* =========================================================
   SMALL METRIC
========================================================= */

function smallMetric(
    title,
    value
) {

    return `

        <div style="
            padding: 10px;
            border-radius: 11px;
            background: rgba(0,0,0,0.025);
        ">

            <div style="
                font-size: 9px;
                opacity: 0.5;
                margin-bottom: 4px;
            ">
                ${title}
            </div>

            <div style="
                font-size: 14px;
                font-weight: 800;
            ">
                ${value}
            </div>

        </div>

    `;

}


/* =========================================================
   DEPARTMENT CHART
========================================================= */

function renderDepartmentChart(
    employees
) {

    const container =
        document.getElementById(
            "departmentChart"
        );


    if (!container) {

        return;

    }


    if (!employees.length) {

        container.innerHTML = `

            <div class="loading-state">
                No employee data available yet.
            </div>

        `;

        return;

    }


    const departmentCounts = {};


    employees.forEach(
        employee => {

            const department =
                employee.department ||
                "Unassigned";


            if (
                !departmentCounts[department]
            ) {

                departmentCounts[department] =
                    0;

            }


            departmentCounts[department]++;

        }
    );


    const departments =
        Object.entries(
            departmentCounts
        )
        .sort(
            (a, b) =>
                b[1] - a[1]
        );


    const maximum =
        departments[0][1];


    container.innerHTML = "";


    departments.forEach(
        ([department, count]) => {

            const percentage =
                (count / maximum) * 100;


            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "department-row";


            row.innerHTML = `

                <div class="department-name">
                    ${escapeHTML(
                        department
                    )}
                </div>

                <div class="department-bar">

                    <div
                        class="department-progress"
                        style="width: ${percentage}%"
                    ></div>

                </div>

                <div class="department-count">
                    ${count}
                </div>

            `;


            container.appendChild(
                row
            );

        }
    );

}


/* =========================================================
   EMPLOYEE TABLE
========================================================= */

function renderEmployeeTable(
    employees
) {

    const tableBody =
        document.getElementById(
            "employeeTableBody"
        );


    if (!tableBody) {

        return;

    }


    if (!employees.length) {

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="5"
                    class="loading-table"
                >
                    No employees found.
                </td>

            </tr>

        `;

        return;

    }


    tableBody.innerHTML = "";


    employees.forEach(
        employee => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>

                    <div class="employee-name">
                        ${escapeHTML(
                            employee.employee_code
                        )}
                    </div>

                    <div class="employee-code">
                        ID #${employee.id}
                    </div>

                </td>

                <td>
                    ${escapeHTML(
                        employee.department ||
                        "-"
                    )}
                </td>

                <td>
                    ${escapeHTML(
                        employee.designation ||
                        "-"
                    )}
                </td>

                <td>
                    ${formatDate(
                        employee.joining_date
                    )}
                </td>

                <td>

                    <span class="status-badge">
                        ${escapeHTML(
                            employee.status ||
                            "unknown"
                        )}
                    </span>

                </td>

            `;


            tableBody.appendChild(
                row
            );

        }
    );

}


/* =========================================================
   SEARCH EMPLOYEES
========================================================= */

function filterEmployees() {

    const searchInput =
        document.getElementById(
            "employeeSearch"
        );


    if (!searchInput) {

        return;

    }


    const search =
        searchInput.value
            .trim()
            .toLowerCase();


    if (!search) {

        renderEmployeeTable(
            allEmployees
        );

        return;

    }


    const filtered =
        allEmployees.filter(
            employee => {

                return (

                    String(
                        employee.employee_code ||
                        ""
                    )
                    .toLowerCase()
                    .includes(search)

                    ||

                    String(
                        employee.department ||
                        ""
                    )
                    .toLowerCase()
                    .includes(search)

                    ||

                    String(
                        employee.designation ||
                        ""
                    )
                    .toLowerCase()
                    .includes(search)

                );

            }
        );


    renderEmployeeTable(
        filtered
    );

}


/* =========================================================
   LOGOUT
========================================================= */

async function logout() {

    try {

        if (
            window.google &&
            window.google.accounts &&
            window.google.accounts.id
        ) {

            google.accounts.id.disableAutoSelect();

        }


        const response =
            await fetch(
                "/logout",
                {
                    method: "POST",

                    credentials:
                        "same-origin"
                }
            );


        if (response.ok) {

            window.location.href =
                "/app";

        }

    } catch (error) {

        console.error(
            "Logout error:",
            error
        );


        alert(
            "Unable to logout. Please try again."
        );

    }

}


/* =========================================================
   INITIALS
========================================================= */

function getInitials(name) {

    if (!name) {

        return "HR";

    }


    const words =
        name.trim().split(/\s+/);


    if (words.length === 1) {

        return words[0]
            .substring(0, 2)
            .toUpperCase();

    }


    return (
        words[0][0] +
        words[words.length - 1][0]
    ).toUpperCase();

}


/* =========================================================
   DATE FORMAT
========================================================= */

function formatDate(dateString) {

    if (!dateString) {

        return "-";

    }


    const date =
        new Date(dateString);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return dateString;

    }


    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );

}


/* =========================================================
   SET ELEMENT TEXT
========================================================= */

function setElementText(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value;

    }

}


/* =========================================================
   SECURITY HELPER
========================================================= */

function escapeHTML(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(value ?? "");


    return div.innerHTML;

}


/* =========================================================
   TEMPORARY ADD EMPLOYEE BUTTON
========================================================= */

function showComingSoon() {

    alert(
        "Employee creation is already available through the HR API. We will connect this button to the dashboard form next."
    );

}