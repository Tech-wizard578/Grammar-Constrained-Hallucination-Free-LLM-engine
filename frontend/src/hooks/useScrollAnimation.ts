import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

interface ScrollAnimationOptions {
    /** Animation type */
    type?: "fadeIn" | "slideUp" | "slideLeft" | "slideRight" | "scale" | "reveal";
    /** Delay before animation starts (seconds) */
    delay?: number;
    /** Animation duration (seconds) */
    duration?: number;
    /** Start position relative to viewport (e.g., "top 80%") */
    start?: string;
    /** Whether to only play once or replay on scroll */
    once?: boolean;
    /** Stagger delay for child elements (seconds) */
    stagger?: number;
    /** Selector for staggering child elements */
    staggerSelector?: string;
}

const defaultOptions: ScrollAnimationOptions = {
    type: "fadeIn",
    delay: 0,
    duration: 0.8,
    start: "top 85%",
    once: true,
    stagger: 0.1,
};

/**
 * Custom hook for GSAP scroll-triggered animations
 * 
 * @example
 * // Basic fade in
 * const ref = useScrollAnimation<HTMLDivElement>();
 * return <div ref={ref}>Content</div>
 * 
 * @example
 * // Staggered children
 * const ref = useScrollAnimation<HTMLDivElement>({ 
 *   type: "slideUp", 
 *   staggerSelector: ".card" 
 * });
 * return <div ref={ref}><div className="card">1</div><div className="card">2</div></div>
 */
export function useScrollAnimation<T extends HTMLElement>(
    options: ScrollAnimationOptions = {}
) {
    const ref = useRef<T>(null);
    const opts = { ...defaultOptions, ...options };

    useEffect(() => {
        const element = ref.current;
        if (!element) return;

        // Define animation properties based on type
        const getAnimationProps = () => {
            switch (opts.type) {
                case "slideUp":
                    return { y: 60, opacity: 0 };
                case "slideLeft":
                    return { x: 60, opacity: 0 };
                case "slideRight":
                    return { x: -60, opacity: 0 };
                case "scale":
                    return { scale: 0.9, opacity: 0 };
                case "reveal":
                    return { y: 30, opacity: 0, filter: "blur(10px)" };
                case "fadeIn":
                default:
                    return { opacity: 0 };
            }
        };

        const fromProps = getAnimationProps();
        const toProps = {
            ...Object.fromEntries(
                Object.keys(fromProps).map((key) => [
                    key,
                    key === "opacity" ? 1 : key === "scale" ? 1 : key === "filter" ? "blur(0px)" : 0,
                ])
            ),
            duration: opts.duration,
            delay: opts.delay,
            ease: "power3.out",
        };

        let animation: gsap.core.Tween | gsap.core.Timeline;

        if (opts.staggerSelector) {
            // Staggered animation for children
            const children = element.querySelectorAll(opts.staggerSelector);
            if (children.length > 0) {
                gsap.set(children, fromProps);
                animation = gsap.to(children, {
                    ...toProps,
                    stagger: opts.stagger,
                    scrollTrigger: {
                        trigger: element,
                        start: opts.start,
                        toggleActions: opts.once ? "play none none none" : "play reverse play reverse",
                    },
                });
            } else {
                return;
            }
        } else {
            // Single element animation
            gsap.set(element, fromProps);
            animation = gsap.to(element, {
                ...toProps,
                scrollTrigger: {
                    trigger: element,
                    start: opts.start,
                    toggleActions: opts.once ? "play none none none" : "play reverse play reverse",
                },
            });
        }

        // Cleanup
        return () => {
            if (animation) {
                animation.kill();
            }
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === element) {
                    trigger.kill();
                }
            });
        };
    }, [opts.type, opts.delay, opts.duration, opts.start, opts.once, opts.stagger, opts.staggerSelector]);

    return ref;
}

/**
 * Hook for header scroll effects (background opacity, shrink)
 */
export function useHeaderScroll() {
    const ref = useRef<HTMLElement>(null);

    useEffect(() => {
        const element = ref.current;
        if (!element) return;

        const animation = gsap.to(element, {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            backdropFilter: "blur(20px)",
            borderBottom: "1px solid rgba(255, 255, 255, 0.05)",
            scrollTrigger: {
                trigger: document.body,
                start: "top top",
                end: "100px top",
                scrub: true,
            },
        });

        return () => {
            animation.kill();
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === document.body) {
                    trigger.kill();
                }
            });
        };
    }, []);

    return ref;
}

/**
 * Hook for parallax scrolling effects
 */
export function useParallax<T extends HTMLElement>(speed: number = 0.5) {
    const ref = useRef<T>(null);

    useEffect(() => {
        const element = ref.current;
        if (!element) return;

        const animation = gsap.to(element, {
            y: () => -100 * speed,
            ease: "none",
            scrollTrigger: {
                trigger: element,
                start: "top bottom",
                end: "bottom top",
                scrub: true,
            },
        });

        return () => {
            animation.kill();
        };
    }, [speed]);

    return ref;
}
