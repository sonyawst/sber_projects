
// Подсветка активного пункта меню
function highlightActiveMenu() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const menuLinks = document.querySelectorAll('nav a');
    
    menuLinks.forEach(link => {
        const linkPage = link.getAttribute('href');
        if (linkPage === currentPage) {
            link.setAttribute('aria-current', 'page');
            link.style.backgroundColor = '#005999';
            link.style.fontWeight = 'bold';
        } else {
            link.removeAttribute('aria-current');
        }
    });
}

// Модальное окно для врачей
function initDoctorsModal() {
    const doctorCards = document.querySelectorAll('.doctor-card');
    
    doctorCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Не открываем модалку при клике на ссылки или кнопки
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') return;
            
            const name = this.querySelector('h3').textContent;
            const specialization = this.querySelector('.specialization').textContent;
            const experience = this.querySelector('.experience').textContent;
            const bio = this.querySelector('.bio').textContent;
            const photoSrc = this.querySelector('img').src;
            
            showDoctorModal(name, specialization, experience, bio, photoSrc);
        });
    });
}

// Показ модального окна с информацией о враче
function showDoctorModal(name, specialization, experience, bio, photoSrc) {
    // Создаем модальное окно
    const modal = document.createElement('div');
    modal.className = 'doctor-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    modal.innerHTML = `
        <div class="modal-content" style="
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            transform: scale(0.8);
            transition: transform 0.3s ease;
        ">
            <button class="close-modal" style="
                position: absolute;
                top: 15px;
                right: 15px;
                background: #ff4757;
                color: white;
                border: none;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">×</button>
            
            <div class="modal-photo" style="
                text-align: center;
                margin-bottom: 20px;
            ">
                <img src="${photoSrc}" alt="${name}" style="
                    width: 150px;
                    height: 150px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 4px solid #007acc;
                ">
            </div>
            
            <h2 style="color: #2c3e50; margin-bottom: 10px; text-align: center;">${name}</h2>
            <p class="modal-specialization" style="
                color: #007acc;
                font-weight: bold;
                text-align: center;
                margin-bottom: 10px;
                font-size: 1.1em;
            ">${specialization}</p>
            <p class="modal-experience" style="
                color: #7f8c8d;
                text-align: center;
                margin-bottom: 20px;
            ">${experience}</p>
            <div class="modal-bio" style="
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #007acc;
            ">
                <h3 style="color: #2c3e50; margin-top: 0;">О специалисте:</h3>
                <p style="line-height: 1.6; margin: 0;">${bio}</p>
            </div>
            
            <div class="modal-actions" style="
                margin-top: 20px;
                text-align: center;
            ">
                <button class="btn-appointment" style="
                    background: #28a745;
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-right: 10px;
                ">Записаться на прием</button>
                <button class="btn-close" style="
                    background: #6c757d;
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                ">Закрыть</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Анимация появления
    setTimeout(() => {
        modal.style.opacity = '1';
        modal.querySelector('.modal-content').style.transform = 'scale(1)';
    }, 10);
    
    // Обработчики закрытия
    const closeModal = () => {
        modal.style.opacity = '0';
        modal.querySelector('.modal-content').style.transform = 'scale(0.8)';
        setTimeout(() => {
            document.body.removeChild(modal);
        }, 300);
    };
    
    modal.querySelector('.close-modal').addEventListener('click', closeModal);
    modal.querySelector('.btn-close').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    // Обработчик записи на прием
    modal.querySelector('.btn-appointment').addEventListener('click', () => {
        alert(`Запись к ${name} будет доступна в ближайшее время!`);
        closeModal();
    });
    
    // Закрытие по ESC
    const handleEscape = (e) => {
        if (e.key === 'Escape') closeModal();
    };
    document.addEventListener('keydown', handleEscape);
    
    // Удаляем обработчик после закрытия
    modal.addEventListener('transitionend', () => {
        if (modal.style.opacity === '0') {
            document.removeEventListener('keydown', handleEscape);
        }
    });
}

// ===== ВАЛИДАЦИЯ ФОРМЫ =====

// REGEX для email
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

// Валидация формы
function initFormValidation() {
    const form = document.querySelector('.appointment-form form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const service = document.getElementById('service').value;
        const date = document.getElementById('date').value;
        const message = document.getElementById('message').value.trim();
        
        // Сбрасываем предыдущие ошибки
        clearErrors();
        
        let isValid = true;
        
        // Валидация имени
        if (!name) {
            showError('name', 'Пожалуйста, введите ваше имя');
            isValid = false;
        } else if (name.length < 2) {
            showError('name', 'Имя должно содержать минимум 2 символа');
            isValid = false;
        }
        
        // Валидация телефона
        if (!phone) {
            showError('phone', 'Пожалуйста, введите ваш телефон');
            isValid = false;
        } else if (!isValidPhone(phone)) {
            showError('phone', 'Введите корректный номер телефона');
            isValid = false;
        }
        
        // Валидация услуги
        if (!service) {
            showError('service', 'Пожалуйста, выберите услугу');
            isValid = false;
        }
        
        // Валидация даты
        if (!date) {
            showError('date', 'Пожалуйста, выберите желаемую дату');
            isValid = false;
        } else if (!isValidDate(date)) {
            showError('date', 'Выберите корректную дату');
            isValid = false;
        }
        
        if (isValid) {
            // Имитация отправки формы
            showSuccessMessage();
            form.reset();
        }
    });
    
    // Реальная валидация при вводе
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
}

// Валидация телефона
function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

// Валидация даты
function isValidDate(dateString) {
    const selectedDate = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return selectedDate >= today;
}

// Показать ошибку
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const formGroup = field.closest('.form-group');
    
    let errorElement = formGroup.querySelector('.error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        formGroup.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    field.style.borderColor = '#dc3545';
}

// Очистить ошибки
function clearErrors() {
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(error => error.remove());
    
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.style.borderColor = '#ddd';
    });
}

// Очистить ошибку для конкретного поля
function clearFieldError(field) {
    const formGroup = field.closest('.form-group');
    const errorElement = formGroup.querySelector('.error-message');
    if (errorElement) {
        errorElement.remove();
    }
    field.style.borderColor = '#ddd';
}

// Валидация отдельного поля
function validateField(field) {
    const value = field.value.trim();
    const fieldId = field.id;
    
    clearFieldError(field);
    
    switch (fieldId) {
        case 'name':
            if (!value) {
                showError(fieldId, 'Пожалуйста, введите ваше имя');
            } else if (value.length < 2) {
                showError(fieldId, 'Имя должно содержать минимум 2 символа');
            }
            break;
            
        case 'phone':
            if (!value) {
                showError(fieldId, 'Пожалуйста, введите ваш телефон');
            } else if (!isValidPhone(value)) {
                showError(fieldId, 'Введите корректный номер телефона');
            }
            break;
            
        case 'service':
            if (!value) {
                showError(fieldId, 'Пожалуйста, выберите услугу');
            }
            break;
            
        case 'date':
            if (!value) {
                showError(fieldId, 'Пожалуйста, выберите желаемую дату');
            } else if (!isValidDate(value)) {
                showError(fieldId, 'Выберите корректную дату');
            }
            break;
    }
}

// Показать сообщение об успехе
function showSuccessMessage() {
    const form = document.querySelector('.appointment-form');
    const existingMessage = form.querySelector('.success-message');
    if (existingMessage) existingMessage.remove();
    
    const successMessage = document.createElement('div');
    successMessage.className = 'success-message';
    successMessage.style.cssText = `
        background: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin-top: 20px;
        text-align: center;
    `;
    successMessage.innerHTML = `
        <strong>Успешно!</strong> Ваша заявка принята. Мы свяжемся с вами в ближайшее время для подтверждения записи.
    `;
    
    form.appendChild(successMessage);
    
    // Автоматически скрыть через 5 секунд
    setTimeout(() => {
        successMessage.remove();
    }, 5000);
}

// ===== ИНИЦИАЛИЗАЦИЯ ВСЕХ ФУНКЦИЙ =====
document.addEventListener('DOMContentLoaded', function() {
    // Всегда подсвечиваем активное меню
    highlightActiveMenu();
    
    // Инициализация модалки для врачей (только на странице врачей)
    if (window.location.pathname.includes('doctors.html')) {
        initDoctorsModal();
    }
    
    // Инициализация валидации формы (только на странице контактов)
    if (window.location.pathname.includes('contacts.html')) {
        initFormValidation();
    }
    
    console.log('Медицинский центр "Здоровье" - все системы работают! 🩺');
});