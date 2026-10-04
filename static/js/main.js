document.addEventListener("DOMContentLoaded", () => {

    /* ================================
       HEADER SCROLL
    ================================= */

    const header = document.querySelector(".site-header");

    const handleHeaderScroll = () => {
        if (!header) return;

        if (window.scrollY > 40) {
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }
    };

    handleHeaderScroll();
    window.addEventListener("scroll", handleHeaderScroll, {
        passive: true
    });


    /* ================================
       MOBILE NAVIGATION
    ================================= */

    const menuToggle = document.querySelector(".menu-toggle");
    const mobileNav = document.querySelector(".mobile-nav");

    const closeMobileMenu = () => {
        if (!menuToggle || !mobileNav) return;

        menuToggle.classList.remove("active");
        mobileNav.classList.remove("active");
        document.body.classList.remove("menu-open");
    };

    if (menuToggle && mobileNav) {

        menuToggle.addEventListener("click", () => {

            const isOpen =
                mobileNav.classList.contains("active");

            if (isOpen) {
                closeMobileMenu();
            } else {
                menuToggle.classList.add("active");
                mobileNav.classList.add("active");
                document.body.classList.add("menu-open");
            }
        });

        mobileNav.querySelectorAll("a").forEach(link => {

            link.addEventListener("click", () => {
                closeMobileMenu();
            });

        });
    }


    /* ================================
       ESCAPE KEY
    ================================= */

    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            closeMobileMenu();
        }

    });


    /* ================================
       SCROLL REVEAL
    ================================= */

    const revealElements =
        document.querySelectorAll(".reveal");

    if ("IntersectionObserver" in window) {

        const revealObserver =
            new IntersectionObserver(
                (entries, observer) => {

                    entries.forEach(entry => {

                        if (entry.isIntersecting) {

                            entry.target.classList.add(
                                "visible"
                            );

                            observer.unobserve(
                                entry.target
                            );
                        }

                    });

                },
                {
                    threshold: 0.12
                }
            );

        revealElements.forEach(element => {
            revealObserver.observe(element);
        });

    } else {

        revealElements.forEach(element => {
            element.classList.add("visible");
        });

    }


    /* ================================
       CINEMATIC CURSOR GLOW
    ================================= */

    const finePointer =
        window.matchMedia(
            "(pointer: fine)"
        ).matches;

    if (finePointer) {

        const cursorGlow =
            document.createElement("div");

        cursorGlow.className =
            "cursor-glow";

        document.body.appendChild(
            cursorGlow
        );

        let mouseX = 0;
        let mouseY = 0;
        let glowX = 0;
        let glowY = 0;

        document.addEventListener(
            "mousemove",
            (event) => {

                mouseX = event.clientX;
                mouseY = event.clientY;

            },
            { passive: true }
        );

        const animateCursor = () => {

            glowX +=
                (mouseX - glowX) * 0.12;

            glowY +=
                (mouseY - glowY) * 0.12;

            cursorGlow.style.transform =
                `translate3d(${glowX}px, ${glowY}px, 0)`;

            requestAnimationFrame(
                animateCursor
            );
        };

        animateCursor();
    }


    /* ================================
       SMOOTH ANCHOR SCROLL
    ================================= */

    document
        .querySelectorAll('a[href^="#"]')
        .forEach(link => {

            link.addEventListener(
                "click",
                (event) => {

                    const targetId =
                        link.getAttribute("href");

                    if (
                        !targetId ||
                        targetId === "#"
                    ) {
                        return;
                    }

                    const target =
                        document.querySelector(
                            targetId
                        );

                    if (!target) return;

                    event.preventDefault();

                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }
            );

        });


    /* ================================
       CONTACT FORM
       ONLY HANDLES THE FORM
    ================================= */

    const contactForm =
        document.querySelector(
            ".contact-form"
        );

    if (contactForm) {

        const submitButton =
            contactForm.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

        let originalButtonText =
            submitButton
                ? submitButton.textContent
                : "Send Enquiry";


        contactForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();

                if (!submitButton) return;


                /* Prevent double submissions */

                if (
                    submitButton.disabled
                ) {
                    return;
                }


                /* Collect form data */

                const formData =
                    new FormData(contactForm);

                const enquiry = {

                    name:
                        String(
                            formData.get("name") || ""
                        ).trim(),

                    email:
                        String(
                            formData.get("email") || ""
                        ).trim(),

                    project:
                        String(
                            formData.get("project") || ""
                        ).trim(),

                    budget:
                        String(
                            formData.get("budget") || ""
                        ).trim(),

                    message:
                        String(
                            formData.get("message") || ""
                        ).trim()
                };


                /* Basic browser-side validation */

                if (
                    !enquiry.name ||
                    !enquiry.email ||
                    !enquiry.message
                ) {

                    showFormMessage(
                        contactForm,
                        "Please complete your name, email and message.",
                        false
                    );

                    return;
                }


                /* Sending state */

                submitButton.disabled = true;

                submitButton.textContent =
                    "Sending...";


                try {

                    const response =
                        await fetch(
                            "/api/contact",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify(
                                        enquiry
                                    )
                            }
                        );


                    let result = {};

                    try {

                        result =
                            await response.json();

                    } catch {
                        result = {};
                    }


                    if (!response.ok) {

                        throw new Error(
                            result.detail ||
                            "Unable to send enquiry."
                        );
                    }


                    /* SUCCESS */

                    contactForm.reset();

                    submitButton.textContent =
                        "Enquiry Received ✓";


                    showFormMessage(
                        contactForm,
                        "Thank you. Your enquiry has been received successfully.",
                        true
                    );


                    /* Restore button after a few seconds */

                    setTimeout(() => {

                        submitButton.disabled =
                            false;

                        submitButton.textContent =
                            originalButtonText;

                    }, 4000);


                } catch (error) {

                    console.error(
                        "Contact form error:",
                        error
                    );


                    submitButton.disabled =
                        false;

                    submitButton.textContent =
                        "Try Again";


                    showFormMessage(
                        contactForm,
                        "Something went wrong. Please try again.",
                        false
                    );

                }

            }
        );
    }


    /* ================================
       FORM MESSAGE HELPER
    ================================= */

    function showFormMessage(
        form,
        message,
        success
    ) {

        let messageElement =
            form.querySelector(
                ".form-status"
            );


        if (!messageElement) {

            messageElement =
                document.createElement("div");

            messageElement.className =
                "form-status";

            messageElement.setAttribute(
                "role",
                "status"
            );

            messageElement.setAttribute(
                "aria-live",
                "polite"
            );


            const button =
                form.querySelector(
                    'button[type="submit"], input[type="submit"]'
                );

            if (button) {

                button.parentNode.insertBefore(
                    messageElement,
                    button
                );

            } else {

                form.appendChild(
                    messageElement
                );
            }
        }


        messageElement.textContent =
            message;

        messageElement.classList.remove(
            "success",
            "error"
        );

        messageElement.classList.add(
            success
                ? "success"
                : "error"
        );

        messageElement.style.display =
            "block";


        if (!success) {

            setTimeout(() => {

                if (
                    messageElement
                ) {

                    messageElement.style.display =
                        "none";
                }

            }, 5000);
        }
    }


    /* ================================
       PAGE READY
    ================================= */

    document.body.classList.add(
        "page-ready"
    );

});
