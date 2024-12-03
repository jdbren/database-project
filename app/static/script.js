function setBenefitsEnabled() {
    let employment_type = document.getElementById('employment_type');
    let benefits = document.getElementsByName('benefits');
    benefits.forEach(benefit => {
        benefit.disabled = employment_type.value !== 'Full-Time';
        if (benefit.disabled) benefit.checked = false;
    });
    company_ins = document.getElementById('company_ins_opt');
    if (employment_type.value !== 'Full-Time') {
        company_ins.selected = false
        company_ins.disabled = true
    }
    else
        document.getElementById('company_ins_opt').disabled = false
}

function formatSSN() {
    let ssn = document.getElementById('ssn');
    let ssnValue = ssn.value;
    if (ssnValue.length === 3 || ssnValue.length === 6)
        ssn.value += '-';
}

function formatPhone() {
    let phone = document.getElementById('phone');
    let phoneValue = phone.value;
    if (phoneValue.length === 3)
        phone.value += ' ';
    if (phoneValue.length === 7)
        phone.value += '-';
}
