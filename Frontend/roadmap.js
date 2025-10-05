document.addEventListener('DOMContentLoaded', function() {
    const roadmapSVGContainer = document.getElementById('roadmapSVGContainer');
    const roadmapDataString = sessionStorage.getItem('roadmapData');

    if (!roadmapDataString) {
        roadmapSVGContainer.innerHTML = '<p>Error: No roadmap data found.</p>';
        return;
    }

    let roadmapData;
    try {
        roadmapData = JSON.parse(roadmapDataString);
    } catch (e) {
        roadmapSVGContainer.innerHTML = '<p>Error: Malformed roadmap JSON data.</p>';
        console.error('Malformed roadmap JSON:', e);
        return;
    }

    // Helper to create SVG elements
    function createSVGElement(tag, attributes) {
        const element = document.createElementNS("http://www.w3.org/2000/svg", tag);
        for (const key in attributes) {
            element.setAttribute(key, attributes[key]);
        }
        return element;
    }

    // Text wrapping/truncation helper
    function wrapText(text, maxWidth) {
        if (text.length <= maxWidth) return text;
        return text.substring(0, maxWidth - 3) + '...';
    }

    // Calculate total height dynamically
    function calculateRoadmapHeight(data) {
        let totalHeight = 150; // top padding
        
        if (!data.roadmap || !data.roadmap.phases) return totalHeight;

        for (const phase of data.roadmap.phases) {
            totalHeight += 120; // phase title space
            
            if (!phase.milestones) continue;

            for (const milestone of phase.milestones) {
                totalHeight += 250; // milestone space
                
                // Calculate subtopic rows needed
                const subtopicCount = (milestone.subtopics || []).length;
                const rowsNeeded = Math.ceil(subtopicCount / 2);
                totalHeight += (rowsNeeded * 110); // space for all subtopic rows
            }
            
            totalHeight += 200; // gap before next phase
        }
        
        return totalHeight + 100; // bottom padding
    }

    const SVG_WIDTH = 1400;
    const SVG_HEIGHT = calculateRoadmapHeight(roadmapData);

    const svg = createSVGElement("svg", {
        width: SVG_WIDTH,
        height: SVG_HEIGHT,
        viewBox: `0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`,
    });
    svg.style.backgroundColor = "var(--background-color)";

    let currentY = 150; // start position with top padding

    if (roadmapData.roadmap && roadmapData.roadmap.phases) {
        roadmapData.roadmap.phases.forEach((phase, phaseIndex) => {
            const phaseGroup = createSVGElement("g", {
                class: "phase-group",
                style: `--phase-index: ${phaseIndex}`
            });
            svg.appendChild(phaseGroup);

            // Phase title
            const phaseTitleY = currentY;
            const phaseTitle = createSVGElement("text", {
                x: SVG_WIDTH / 2,
                y: phaseTitleY,
                "font-size": "28px",
                "font-weight": "700",
                "text-anchor": "middle",
                fill: "var(--text-primary)",
                filter: "url(#text-shadow)" // Apply text shadow
            });
            phaseTitle.textContent = phase.phase_name || `Phase ${phaseIndex + 1}`;
            phaseGroup.appendChild(phaseTitle);

            currentY += 120; // Space below phase title
            const phaseLineStart = currentY;

            let milestoneMaxY = currentY; // Track max Y for phase line end

            if (phase.milestones) {
                phase.milestones.forEach((milestone, milestoneIndex) => {
                    const milestoneY = currentY;

                    // Milestone Box
                    const milestoneRectX = SVG_WIDTH / 2 - 250 / 2; // Centered
                    const milestoneRect = createSVGElement("rect", {
                        x: milestoneRectX,
                        y: milestoneY,
                        width: 250,
                        height: 56,
                        fill: "url(#milestone-gradient)", // Apply gradient
                        stroke: "var(--border-dark)",
                        "stroke-width": 3,
                        rx: 8,
                        filter: "url(#box-shadow-milestone)" // Apply box shadow
                    });
                    phaseGroup.appendChild(milestoneRect);

                    // Milestone Text
                    const milestoneText = createSVGElement("text", {
                        x: SVG_WIDTH / 2,
                        y: milestoneY + 56 / 2, // Center of rectangle
                        "font-size": "16px",
                        "font-weight": "600",
                        "text-anchor": "middle",
                        "dominant-baseline": "middle",
                        fill: "var(--text-primary)"
                    });
                    milestoneText.textContent = wrapText(milestone.milestone_title || `Milestone ${milestoneIndex + 1}`, 32);
                    phaseGroup.appendChild(milestoneText);

                    let subtopicCurrentY = milestoneY + 56; // Start subtopics below milestone

                    if (milestone.subtopics) {
                        milestone.subtopics.forEach((subtopic, subtopicIndex) => {
                            const isLeft = subtopicIndex % 2 === 0;
                            const horizontalOffset = 320;
                            const subtopicX = isLeft ? (SVG_WIDTH / 2 - horizontalOffset) : (SVG_WIDTH / 2 + horizontalOffset);
                            const subtopicY = subtopicCurrentY + 120 + (Math.floor(subtopicIndex / 2) * 110);

                            // Subtopic Box
                            const subtopicRectX = subtopicX - 110; // to center the 220px box
                            const subtopicRect = createSVGElement("rect", {
                                x: subtopicRectX,
                                y: subtopicY,
                                width: 220, // Dynamic width (220-300px) - fixed for now
                                height: 50,
                                fill: "url(#subtopic-gradient)", // Apply gradient
                                stroke: "var(--border-dark)",
                                "stroke-width": 2.5,
                                rx: 8,
                                filter: "url(#box-shadow-subtopic)" // Apply box shadow
                            });
                            phaseGroup.appendChild(subtopicRect);

                            // Order Badge (Circular Number)
                            const badgeCircle = createSVGElement("circle", {
                                cx: subtopicRectX + 10,
                                cy: subtopicY + 10,
                                r: 16,
                                fill: "white",
                                stroke: "var(--badge-border)",
                                "stroke-width": 3,
                                filter: "url(#box-shadow-badge)" // Apply box shadow
                            });
                            phaseGroup.appendChild(badgeCircle);

                            const subtopicIdParts = subtopic.subtopic_id ? subtopic.subtopic_id.split('.') : [];
                            const orderNumber = subtopicIdParts.length > 0 ? subtopicIdParts[subtopicIdParts.length - 1] : (subtopicIndex + 1);

                            const badgeText = createSVGElement("text", {
                                x: subtopicRectX + 10,
                                y: subtopicY + 10,
                                "font-size": "13px",
                                "font-weight": "700",
                                "text-anchor": "middle",
                                "dominant-baseline": "middle",
                                fill: "var(--badge-border)"
                            });
                            badgeText.textContent = orderNumber;
                            phaseGroup.appendChild(badgeText);

                            // Subtopic Text
                            const subtopicText = createSVGElement("text", {
                                x: subtopicX,
                                y: subtopicY + 50 / 2, // Center of box
                                "font-size": "14px",
                                "font-weight": "500",
                                "text-anchor": "middle",
                                "dominant-baseline": "middle",
                                fill: "var(--text-secondary)"
                            });
                            subtopicText.textContent = wrapText(subtopic.title || `Subtopic ${subtopicIndex + 1}`, 28);
                            phaseGroup.appendChild(subtopicText);

                            // STEP 5: Connectors (Curved Dotted Lines)
                            const startY = subtopicY + 50 / 2; // Vertical center of subtopic box
                            const endY = milestoneY + 56 / 2; // Vertical center of milestone box

                            let pathD;
                            if (isLeft) {
                                const startX = subtopicRectX + 220; // right edge of left subtopic
                                const endX = milestoneRectX; // left edge of milestone
                                const controlPointOffset = Math.abs(endX - startX) * 0.35;

                                pathD = `M ${startX},${startY}
                                         C ${startX + controlPointOffset},${startY}
                                           ${endX - controlPointOffset},${endY}
                                           ${endX},${endY}`;
                            } else {
                                const startX = subtopicRectX; // left edge of right subtopic
                                const endX = milestoneRectX + 250; // right edge of milestone
                                const controlPointOffset = Math.abs(endX - startX) * 0.35;

                                pathD = `M ${startX},${startY}
                                         C ${startX - controlPointOffset},${startY}
                                           ${endX + controlPointOffset},${endY}
                                           ${endX},${endY}`;
                            }

                            const connectorPath = createSVGElement("path", {
                                d: pathD,
                                stroke: "var(--connector-color)",
                                "stroke-width": 3,
                                "stroke-dasharray": "6 9",
                                fill: "none",
                                "stroke-linecap": "round",
                                "stroke-linejoin": "round",
                                "stroke-opacity": "var(--connector-opacity)",
                                filter: "url(#connector-glow)" // Apply glow
                            });
                            phaseGroup.appendChild(connectorPath);

                            milestoneMaxY = Math.max(milestoneMaxY, subtopicY + 50); // Update max Y for phase line
                        });
                    }

                    // Calculate space needed for this milestone's subtopics
                    const subtopicCount = (milestone.subtopics || []).length;
                    const rowsNeeded = Math.ceil(subtopicCount / 2);
                    const subtopicSectionHeight = (rowsNeeded > 0 ? (120 + (rowsNeeded - 1) * 110 + 50) : 0); // 120 for first row, then 110 for subsequent, +50 for box height

                    currentY = milestoneY + Math.max(250, subtopicSectionHeight + 50); // milestone spacing
                });
            }

            // Phase Line (Vertical)
            const phaseLine = createSVGElement("line", {
                x1: SVG_WIDTH / 2,
                y1: phaseLineStart,
                x2: SVG_WIDTH / 2,
                y2: currentY - 130, // Adjust end Y based on new spacing
                stroke: "var(--phase-line-color)",
                "stroke-width": 5,
                "stroke-linecap": "round",
                "stroke-opacity": "var(--phase-line-opacity)",
                filter: "url(#phase-line-glow)" // Apply glow
            });
            phaseGroup.appendChild(phaseLine);

            currentY += 200; // 200px gap before next phase
        });
    }

    // Define SVG Filters and Gradients
    const defs = createSVGElement("defs", {});

    // Text Shadow Filter
    const textShadowFilter = createSVGElement("filter", { id: "text-shadow" });
    textShadowFilter.innerHTML = '<feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur" />' +
                                 '<feOffset in="blur" dx="0" dy="2" result="offsetBlur" />' +
                                 '<feFlood flood-color="rgba(0,0,0,0.08)" result="color" />' +
                                 '<feComposite in="color" in2="offsetBlur" operator="in" result="shadow" />' +
                                 '<feMerge>' +
                                 '<feMergeNode in="shadow" />' +
                                 '<feMergeNode in="SourceGraphic" />' +
                                 '</feMerge>';
    defs.appendChild(textShadowFilter);

    // Box Shadow Filter (Milestone)
    const boxShadowMilestoneFilter = createSVGElement("filter", { id: "box-shadow-milestone" });
    boxShadowMilestoneFilter.innerHTML = '<feGaussianBlur in="SourceAlpha" stdDeviation="4" result="blur" />' +
                                         '<feOffset in="blur" dx="0" dy="4" result="offsetBlur" />' +
                                         '<feFlood flood-color="rgba(0,0,0,0.15)" result="color" />' +
                                         '<feComposite in="color" in2="offsetBlur" operator="in" result="shadow" />' +
                                         '<feMerge>' +
                                         '<feMergeNode in="shadow" />' +
                                         '<feMergeNode in="SourceGraphic" />' +
                                         '</feMerge>';
    defs.appendChild(boxShadowMilestoneFilter);

    // Box Shadow Filter (Subtopic)
    const boxShadowSubtopicFilter = createSVGElement("filter", { id: "box-shadow-subtopic" });
    boxShadowSubtopicFilter.innerHTML = '<feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur" />' +
                                        '<feOffset in="blur" dx="0" dy="3" result="offsetBlur" />' +
                                        '<feFlood flood-color="rgba(0,0,0,0.12)" result="color" />' +
                                        '<feComposite in="color" in2="offsetBlur" operator="in" result="shadow" />' +
                                        '<feMerge>' +
                                        '<feMergeNode in="shadow" />' +
                                        '<feMergeNode in="SourceGraphic" />' +
                                        '</feMerge>';
    defs.appendChild(boxShadowSubtopicFilter);

    // Box Shadow Filter (Badge)
    const boxShadowBadgeFilter = createSVGElement("filter", { id: "box-shadow-badge" });
    boxShadowBadgeFilter.innerHTML = '<feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur" />' +
                                     '<feOffset in="blur" dx="0" dy="2" result="offsetBlur" />' +
                                     '<feFlood flood-color="rgba(0,0,0,0.2)" result="color" />' +
                                     '<feComposite in="color" in2="offsetBlur" operator="in" result="shadow" />' +
                                     '<feMerge>' +
                                     '<feMergeNode in="shadow" />' +
                                     '<feMergeNode in="SourceGraphic" />' +
                                     '</feMerge>';
    defs.appendChild(boxShadowBadgeFilter);

    // Phase Line Glow Filter
    const phaseLineGlowFilter = createSVGElement("filter", { id: "phase-line-glow" });
    phaseLineGlowFilter.innerHTML = '<feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />' +
                                    '<feFlood flood-color="rgba(43,120,228,0.2)" result="color" />' +
                                    '<feComposite in="color" in2="blur" operator="in" result="glow" />' +
                                    '<feMerge>' +
                                    '<feMergeNode in="glow" />' +
                                    '<feMergeNode in="SourceGraphic" />' +
                                    '</feMerge>';
    defs.appendChild(phaseLineGlowFilter);

    // Connector Glow Filter
    const connectorGlowFilter = createSVGElement("filter", { id: "connector-glow" });
    connectorGlowFilter.innerHTML = '<feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur" />' +
                                    '<feFlood flood-color="rgba(43,120,228,0.15)" result="color" />' +
                                    '<feComposite in="color" in2="blur" operator="in" result="glow" />' +
                                    '<feMerge>' +
                                    '<feMergeNode in="glow" />' +
                                    '<feMergeNode in="SourceGraphic" />' +
                                    '</feMerge>';
    defs.appendChild(connectorGlowFilter);

    // Gradients
    const milestoneGradient = createSVGElement("linearGradient", { id: "milestone-gradient", x1: "0%", y1: "0%", x2: "0%", y2: "100%" });
    milestoneGradient.innerHTML = '<stop offset="0%" style="stop-color:var(--milestone-bg-start);stop-opacity:1" />' +
                                  '<stop offset="100%" style="stop-color:var(--milestone-bg-end);stop-opacity:1" />';
    defs.appendChild(milestoneGradient);

    const subtopicGradient = createSVGElement("linearGradient", { id: "subtopic-gradient", x1: "0%", y1: "0%", x2: "0%", y2: "100%" });
    subtopicGradient.innerHTML = '<stop offset="0%" style="stop-color:var(--subtopic-bg-start);stop-opacity:1" />' +
                                 '<stop offset="100%" style="stop-color:var(--subtopic-bg-end);stop-opacity:1" />';
    defs.appendChild(subtopicGradient);

    svg.appendChild(defs);

    roadmapSVGContainer.appendChild(svg);

    sessionStorage.removeItem('roadmapData'); // Clean up sessionStorage
});