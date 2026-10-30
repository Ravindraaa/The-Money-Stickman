/* The Money Stickman reusable SVG rig.
 * Loaded by HyperFrames compositions after GSAP. All motion is timeline-driven.
 */
(function (global) {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const markup = `
    <svg class="ms-rig" viewBox="0 0 300 520" role="img" aria-label="Money Stickman">
      <ellipse cx="150" cy="496" rx="78" ry="13" fill="#020817" opacity=".42"/>
      <g class="ms-body">
        <path d="M150 158 L150 335" stroke="#f7fbff" stroke-width="18" stroke-linecap="round"/>
      </g>
      <g class="ms-arm ms-arm-left" transform="translate(142 190)">
        <path d="M0 0 L-53 65" stroke="#f7fbff" stroke-width="17" stroke-linecap="round" fill="none"/>
        <g class="ms-forearm ms-forearm-left" transform="translate(-53 65)">
          <path d="M0 0 L-28 -34" stroke="#f7fbff" stroke-width="16" stroke-linecap="round" fill="none"/>
          <circle cx="-28" cy="-34" r="8" fill="#f7fbff"/>
        </g>
      </g>
      <g class="ms-arm ms-arm-right" transform="translate(158 190)">
        <path d="M0 0 L53 65" stroke="#f7fbff" stroke-width="17" stroke-linecap="round" fill="none"/>
        <g class="ms-forearm ms-forearm-right" transform="translate(53 65)">
          <path d="M0 0 L28 -34" stroke="#f7fbff" stroke-width="16" stroke-linecap="round" fill="none"/>
          <circle cx="28" cy="-34" r="8" fill="#f7fbff"/>
        </g>
      </g>
      <g class="ms-leg ms-leg-left" transform="translate(143 335)">
        <path d="M0 0 L-28 78" stroke="#f7fbff" stroke-width="18" stroke-linecap="round" fill="none"/>
        <g class="ms-shin ms-shin-left" transform="translate(-28 78)">
          <path d="M0 0 L-8 76" stroke="#f7fbff" stroke-width="17" stroke-linecap="round" fill="none"/>
          <path d="M-8 76 L-35 76" stroke="#f7fbff" stroke-width="17" stroke-linecap="round"/>
        </g>
      </g>
      <g class="ms-leg ms-leg-right" transform="translate(157 335)">
        <path d="M0 0 L28 78" stroke="#f7fbff" stroke-width="18" stroke-linecap="round" fill="none"/>
        <g class="ms-shin ms-shin-right" transform="translate(28 78)">
          <path d="M0 0 L8 76" stroke="#f7fbff" stroke-width="17" stroke-linecap="round" fill="none"/>
          <path d="M8 76 L35 76" stroke="#f7fbff" stroke-width="17" stroke-linecap="round"/>
        </g>
      </g>
      <circle class="ms-head" cx="150" cy="91" r="67" fill="#f7fbff"/>
      <path class="ms-brow ms-brow-left" d="M117 67 Q130 59 140 67" fill="none" stroke="#0a1630" stroke-width="6" stroke-linecap="round"/>
      <path class="ms-brow ms-brow-right" d="M160 67 Q173 59 183 67" fill="none" stroke="#0a1630" stroke-width="6" stroke-linecap="round"/>
      <ellipse class="ms-eye ms-eye-left" cx="130" cy="91" rx="7" ry="11" fill="#0a1630"/>
      <ellipse class="ms-eye ms-eye-right" cx="170" cy="91" rx="7" ry="11" fill="#0a1630"/>
      <path class="ms-mouth" d="M128 124 Q150 145 172 124" fill="none" stroke="#0a1630" stroke-width="7" stroke-linecap="round"/>
    </svg>`;

  function mount(target) {
    const host = typeof target === "string" ? document.querySelector(target) : target;
    if (!host) throw new Error("MoneyStickman.mount: target not found");
    host.innerHTML = markup;
    const svg = host.querySelector("svg");
    const rig = { host, svg };
    [
      "body", "head", "arm-left", "arm-right", "forearm-left", "forearm-right",
      "leg-left", "leg-right", "shin-left", "shin-right", "mouth",
      "brow-left", "brow-right", "eye-left", "eye-right"
    ].forEach((key) => {
      const selector = ".ms-" + key;
      rig[key] = svg.querySelector(selector);
    });
    gsap.set([rig["arm-left"], rig["arm-right"], rig["leg-left"], rig["leg-right"],
      rig["forearm-left"], rig["forearm-right"], rig["shin-left"], rig["shin-right"]],
      { transformBox: "view-box", transformOrigin: "0px 0px" });
    return rig;
  }

  function expression(rig, name, timeline, at = 0) {
    const faces = {
      neutral: { mouth: "M128 124 Q150 145 172 124", brow: 0, eyes: 11 },
      happy: { mouth: "M122 119 Q150 158 178 119", brow: -3, eyes: 10 },
      surprised: { mouth: "M140 119 Q150 105 160 119 Q160 141 150 145 Q140 141 140 119", brow: -10, eyes: 15 },
      worried: { mouth: "M126 139 Q150 116 174 139", brow: 8, eyes: 9 },
      thinking: { mouth: "M137 132 Q151 126 166 132", brow: -4, eyes: 9 }
    };
    const face = faces[name] || faces.neutral;
    timeline.to(rig.mouth, { attr: { d: face.mouth }, duration: 0.22 }, at);
    timeline.to([rig["brow-left"], rig["brow-right"]], { y: face.brow, duration: 0.22 }, at);
    timeline.to([rig["eye-left"], rig["eye-right"]], { attr: { ry: face.eyes }, duration: 0.22 }, at);
    return timeline;
  }

  function walk(rig, timeline, options = {}) {
    const at = options.at ?? 0;
    const duration = Math.max(0.6, options.duration ?? 2);
    const cycles = Math.max(0, Math.floor(duration / 0.6) - 1);
    const cycle = gsap.timeline({ repeat: cycles, yoyo: true });
    cycle.to(rig["leg-left"], { rotation: 24, duration: 0.3, ease: "sine.inOut" }, 0)
      .to(rig["leg-right"], { rotation: -24, duration: 0.3, ease: "sine.inOut" }, 0)
      .to(rig["arm-left"], { rotation: -22, duration: 0.3, ease: "sine.inOut" }, 0)
      .to(rig["arm-right"], { rotation: 22, duration: 0.3, ease: "sine.inOut" }, 0)
      .to(rig.svg, { y: -9, duration: 0.3, ease: "sine.inOut" }, 0);
    timeline.add(cycle, at);
    return cycle;
  }

  function point(rig, timeline, direction = "right", at = 0) {
    const side = direction === "left" ? "left" : "right";
    timeline.to(rig["arm-" + side], { rotation: side === "right" ? -62 : 62, duration: 0.32, ease: "back.out(1.5)" }, at);
    timeline.to(rig["forearm-" + side], { rotation: side === "right" ? -26 : 26, duration: 0.28 }, at + 0.18);
    expression(rig, "thinking", timeline, at);
    return timeline;
  }

  function react(rig, timeline, emotion = "surprised", at = 0) {
    expression(rig, emotion, timeline, at);
    timeline.to(rig.svg, { y: -18, rotation: emotion === "worried" ? -5 : 4, duration: 0.22, yoyo: true, repeat: 1, ease: "power2.out" }, at);
    timeline.to(rig["arm-left"], { rotation: -28, duration: 0.22, yoyo: true, repeat: 1 }, at);
    timeline.to(rig["arm-right"], { rotation: 28, duration: 0.22, yoyo: true, repeat: 1 }, at);
    return timeline;
  }

  function pickUp(rig, timeline, prop, at = 0) {
    const item = typeof prop === "string" ? document.querySelector(prop) : prop;
    if (!item) throw new Error("MoneyStickman.pickUp: prop not found");
    timeline.to(rig["arm-right"], { rotation: 48, duration: 0.28, ease: "power2.out" }, at);
    timeline.to(rig["forearm-right"], { rotation: -35, duration: 0.22 }, at + 0.18);
    timeline.to(item, { x: 70, y: -80, scale: 0.78, rotation: 12, duration: 0.42, ease: "power2.inOut" }, at + 0.28);
    timeline.to(rig["arm-right"], { rotation: 8, duration: 0.28 }, at + 0.72);
    return timeline;
  }

  function celebrate(rig, timeline, at = 0) {
    expression(rig, "happy", timeline, at);
    timeline.to(rig["arm-left"], { rotation: -125, duration: 0.28, ease: "back.out(1.7)" }, at);
    timeline.to(rig["arm-right"], { rotation: 125, duration: 0.28, ease: "back.out(1.7)" }, at);
    timeline.to(rig.svg, { y: -24, duration: 0.24, yoyo: true, repeat: 3, ease: "sine.inOut" }, at + 0.25);
    return timeline;
  }

  global.MoneyStickman = { mount, expression, walk, point, react, pickUp, celebrate };
})(window);
