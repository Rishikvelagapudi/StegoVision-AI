import React, { useState } from "react";
import {
  ShieldAlert,
  Search,
  Lock,
  FileCheck,
  RotateCcw,
  Sparkles,
  MousePointerClick,
  CheckCircle2,
  AlertTriangle,
  Eye,
  Key,
  Fingerprint,
  FileBadge2,
  Terminal,
} from "lucide-react";

export const COMIC_PANELS = [
  // --- COLUMN 1 (LEFT SIDE) ---
  {
    id: "malware",
    col: "left",
    caseNumber: "CASE #01",
    actionBadge: "ZAP!",
    actionColor: "bg-red-500 text-white",
    title: "The Trojan Meme",
    tagline: "Malware Smuggled in Social Media",
    badge: "Cyber Defense",
    badgeColor: "bg-rose-100 text-rose-800 border-rose-300",
    svg: (
      <svg viewBox="0 0 500 280" className="w-full h-auto select-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="c1bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#1e293b" />
          </linearGradient>
          <linearGradient id="c1beam" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.1" />
            <stop offset="50%" stopColor="#34d399" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0.1" />
          </linearGradient>
        </defs>

        <rect width="500" height="280" fill="url(#c1bg)" />
        {/* Comic halftone pattern */}
        <g opacity="0.15">
          {Array.from({ length: 25 }).map((_, i) => (
            <line key={i} x1={i * 20} y1="0" x2={i * 20} y2="280" stroke="#94a3b8" strokeWidth="1" strokeDasharray="2 6" />
          ))}
        </g>
        <rect x="6" y="6" width="488" height="268" fill="none" stroke="#000" strokeWidth="3" />

        {/* Action Burst */}
        <polygon points="50,15 70,22 85,12 82,30 98,35 84,45 92,60 76,52 68,68 60,52 44,58 50,42 35,32 50,28" fill="#ef4444" stroke="#000" strokeWidth="1.5" />
        <text x="65" y="42" textAnchor="middle" fill="#fff" fontSize="11" fontWeight="900" transform="rotate(-8 65 42)">ZAP!</text>

        {/* Hacker Screen Left */}
        <g transform="translate(25, 40)">
          <rect width="125" height="95" rx="6" fill="#020617" stroke="#ef4444" strokeWidth="2" />
          <rect width="125" height="16" fill="#1e1b4b" rx="6" />
          <circle cx="10" cy="8" r="3" fill="#ef4444" />
          <circle cx="18" cy="8" r="3" fill="#f59e0b" />
          <circle cx="26" cy="8" r="3" fill="#10b981" />
          <text x="8" y="32" fill="#ef4444" fontSize="9" fontFamily="monospace">&gt; hide_c2_botnet()</text>
          <text x="8" y="46" fill="#fca5a5" fontSize="8" fontFamily="monospace">target: cute_cat.png</text>
          <text x="8" y="60" fill="#f87171" fontSize="8" fontFamily="monospace">bits: 01010010 01000001</text>
          <text x="8" y="74" fill="#ef4444" fontSize="8" fontFamily="monospace">[SHELLCODE EMBEDDED]</text>
          <rect x="8" y="80" width="109" height="8" rx="2" fill="#ef4444" opacity="0.3" />
        </g>

        {/* Center: Cute Meme Image */}
        <g transform="translate(185, 30)">
          <rect width="120" height="135" rx="8" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <rect x="8" y="8" width="104" height="85" rx="4" fill="#fef3c7" />
          <circle cx="60" cy="52" r="24" fill="#f59e0b" />
          <polygon points="40,36 48,22 54,34" fill="#d97706" />
          <polygon points="80,36 72,22 66,34" fill="#d97706" />
          <circle cx="52" cy="50" r="3" fill="#000" />
          <circle cx="68" cy="50" r="3" fill="#000" />
          <ellipse cx="60" cy="58" rx="4" ry="2" fill="#ef4444" />
          <text x="60" y="110" textAnchor="middle" fill="#0f172a" fontSize="10" fontWeight="bold">"Harmless Cat"</text>
          <text x="60" y="124" textAnchor="middle" fill="#dc2626" fontSize="8" fontWeight="bold">⚠ INVISIBLE TROJAN</text>
        </g>

        {/* StegoVision Scanner Right */}
        <g transform="translate(335, 35)">
          <rect width="135" height="125" rx="8" fill="#064e3b" stroke="#10b981" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <circle cx="67" cy="62" r="38" fill="none" stroke="#34d399" strokeWidth="1.5" strokeDasharray="3 3" />
          <circle cx="67" cy="62" r="22" fill="none" stroke="#34d399" strokeWidth="1" />
          <path d="M 67 36 L 85 45 L 85 68 Q 67 90 67 90 Q 67 90 49 68 L 49 45 Z" fill="#059669" stroke="#6ee7b7" strokeWidth="2" />
          <path d="M 59 62 L 65 68 L 76 54" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" />
          <text x="67" y="110" textAnchor="middle" fill="#a7f3d0" fontSize="10" fontWeight="bold">STEGOVISION AI</text>
          <text x="67" y="120" textAnchor="middle" fill="#6ee7b7" fontSize="8">PAYLOAD INTERCEPTED</text>
        </g>

        {/* Scanning Laser Beam */}
        <polygon points="335,70 305,50 305,150 335,130" fill="url(#c1beam)" />

        {/* Comic Dialogue Strip at Bottom */}
        <g transform="translate(20, 185)">
          <rect width="460" height="75" rx="6" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 2px 0px #000)" />
          <polygon points="230,0 245,-12 260,0" fill="#fff" stroke="#000" strokeWidth="2" />
          <rect x="231" y="0" width="28" height="4" fill="#fff" />
          <text x="16" y="24" fill="#dc2626" fontSize="12" fontWeight="900">SECURITY BREACH AVERTED IN REAL TIME</text>
          <text x="16" y="44" fill="#334155" fontSize="10.5">
            "Antivirus scanned the meme and approved it. StegoVision inspected pixel bitplanes, spotted hidden C2 shellcode, and extracted it!"
          </text>
          <text x="16" y="62" fill="#059669" fontSize="10" fontWeight="bold">
            👉 CLICK IMAGE TO REVEAL HOW IT WORKS STEP-BY-STEP
          </text>
        </g>
      </svg>
    ),
    points: [
      {
        step: "Step 1: The Concealment",
        title: "Malware Camouflaged in Social Memes",
        desc: "Threat actors inject reverse-shell scripts and ransomware beacons into ordinary PNG and JPEG memes shared across Slack and email gateways.",
        icon: AlertTriangle,
        color: "text-amber-600 bg-amber-50 border-amber-200",
      },
      {
        step: "Step 2: Antivirus Blindspot",
        title: "Perimeter Firewalls Pass It Through",
        desc: "Because the image displays normally and possesses valid container headers, standard signature antivirus rates the weaponized meme clean.",
        icon: Eye,
        color: "text-sky-600 bg-sky-50 border-sky-200",
      },
      {
        step: "Step 3: StegoVision Defense",
        title: "Bit-Plane Extraction Stops Execution",
        desc: "StegoVision AI measures bit-plane variance and extracts the malicious payload, disarming the attack before endpoints can run it.",
        icon: ShieldAlert,
        color: "text-emerald-700 bg-emerald-50 border-emerald-300",
      },
    ],
  },
  {
    id: "exfiltration",
    col: "left",
    caseNumber: "CASE #02",
    actionBadge: "CAUGHT!",
    actionColor: "bg-amber-500 text-slate-900",
    title: "The Silent Exfiltration",
    tagline: "Corporate Espionage & Leaked Blueprints",
    badge: "Data Loss Prevention",
    badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
    svg: (
      <svg viewBox="0 0 500 280" className="w-full h-auto select-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="c2bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#022c22" />
            <stop offset="100%" stopColor="#0f172a" />
          </linearGradient>
        </defs>

        <rect width="500" height="280" fill="url(#c2bg)" />
        <rect x="6" y="6" width="488" height="268" fill="none" stroke="#000" strokeWidth="3" />

        {/* Action Burst */}
        <polygon points="50,15 70,22 85,12 82,30 98,35 84,45 92,60 76,52 68,68 60,52 44,58 50,42 35,32 50,28" fill="#f59e0b" stroke="#000" strokeWidth="1.5" />
        <text x="65" y="42" textAnchor="middle" fill="#000" fontSize="10" fontWeight="900" transform="rotate(-8 65 42)">CAUGHT!</text>

        {/* Blueprint Left */}
        <g transform="translate(25, 45)">
          <rect width="115" height="110" rx="4" fill="#1e3a8a" stroke="#60a5fa" strokeWidth="2" />
          <text x="10" y="24" fill="#93c5fd" fontSize="9" fontWeight="bold">TOP SECRET PATENT</text>
          <line x1="10" y1="32" x2="105" y2="32" stroke="#3b82f6" strokeWidth="1" />
          <circle cx="57" cy="62" r="18" fill="none" stroke="#93c5fd" strokeWidth="1.5" strokeDasharray="3 2" />
          <line x1="20" y1="62" x2="95" y2="62" stroke="#60a5fa" strokeWidth="1" />
          <text x="57" y="100" textAnchor="middle" fill="#bfdbfe" fontSize="8" fontFamily="monospace">AEROSPACE_SPEC.PDF</text>
        </g>

        {/* Encoded Arrow */}
        <g transform="translate(150, 85)">
          <path d="M 0 10 L 22 10 L 22 4 L 34 15 L 22 26 L 22 20 L 0 20 Z" fill="#f59e0b" stroke="#000" strokeWidth="1" />
          <text x="15" y="38" textAnchor="middle" fill="#fbbf24" fontSize="8" fontWeight="bold">ENCODED</text>
        </g>

        {/* Vacation Photo Center */}
        <g transform="translate(195, 35)">
          <rect width="120" height="130" rx="8" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <rect x="8" y="8" width="104" height="85" rx="4" fill="#38bdf8" />
          <circle cx="90" cy="28" r="10" fill="#facc15" />
          <rect x="8" y="55" width="104" height="38" fill="#0284c7" />
          <path d="M 8 75 Q 60 60 112 75 Z" fill="#eab308" />
          <text x="60" y="110" textAnchor="middle" fill="#0f172a" fontSize="10" fontWeight="bold">"Beach_Trip.png"</text>
          <text x="60" y="122" textAnchor="middle" fill="#64748b" fontSize="8">(8 MB PDF hidden)</text>
        </g>

        {/* Evidence Safe Right */}
        <g transform="translate(340, 40)">
          <rect width="130" height="115" rx="8" fill="#064e3b" stroke="#10b981" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <circle cx="65" cy="52" r="24" fill="#022c22" stroke="#34d399" strokeWidth="2" />
          <rect x="56" y="44" width="18" height="18" rx="2" fill="#10b981" />
          <text x="65" y="94" textAnchor="middle" fill="#6ee7b7" fontSize="10" fontWeight="bold">EVIDENCE VAULT</text>
          <text x="65" y="106" textAnchor="middle" fill="#a7f3d0" fontSize="8">PDF Fully Recovered</text>
        </g>

        {/* Comic Dialogue Bottom */}
        <g transform="translate(20, 185)">
          <rect width="460" height="75" rx="6" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 2px 0px #000)" />
          <polygon points="255,0 270,-12 285,0" fill="#fff" stroke="#000" strokeWidth="2" />
          <rect x="256" y="0" width="28" height="4" fill="#fff" />
          <text x="16" y="24" fill="#059669" fontSize="12" fontWeight="900">INSIDER THEFT TRAPPED BY FORENSIC AUDIT</text>
          <text x="16" y="44" fill="#334155" fontSize="10.5">
            "Employee emailed confidential aircraft designs disguised inside a personal photo. StegoVision AI decoded the LSBs and provided court-admissible proof!"
          </text>
          <text x="16" y="62" fill="#059669" fontSize="10" fontWeight="bold">
            👉 CLICK IMAGE TO REVEAL HOW IT WORKS STEP-BY-STEP
          </text>
        </g>
      </svg>
    ),
    points: [
      {
        step: "Step 1: The Insider Threat",
        title: "Sneaking Files Past Corporate DLP",
        desc: "Disgruntled staff compress sensitive customer records and proprietary designs, interleaving the binary bits into the RGB samples of personal photos.",
        icon: Lock,
        color: "text-amber-600 bg-amber-50 border-amber-200",
      },
      {
        step: "Step 2: DLP Avoidance",
        title: "Text Filters Miss Pixel Alterations",
        desc: "Data Loss Prevention (DLP) tools scan text attachments. Converted into pixel LSBs, DLP sees only a standard image file and allows the email out.",
        icon: Eye,
        color: "text-sky-600 bg-sky-50 border-sky-200",
      },
      {
        step: "Step 3: Forensic Proof",
        title: "Full Payload Reconstruction",
        desc: "StegoVision AI detects the modified capacity fraction via RS group analysis, recovering the exact original file with SHA-256 validation.",
        icon: FileCheck,
        color: "text-emerald-700 bg-emerald-50 border-emerald-300",
      },
    ],
  },
  {
    id: "deaddrop",
    col: "left",
    caseNumber: "CASE #03",
    actionBadge: "DECODED!",
    actionColor: "bg-blue-600 text-white",
    title: "The Digital Dead-Drop",
    tagline: "Covert Channels in Public Auction Sites",
    badge: "Digital Forensics",
    badgeColor: "bg-blue-100 text-blue-800 border-blue-300",
    svg: (
      <svg viewBox="0 0 500 280" className="w-full h-auto select-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="c3bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#1e3a8a" />
          </linearGradient>
        </defs>

        <rect width="500" height="280" fill="url(#c3bg)" />
        <rect x="6" y="6" width="488" height="268" fill="none" stroke="#000" strokeWidth="3" />

        {/* Action Burst */}
        <polygon points="50,15 70,22 85,12 82,30 98,35 84,45 92,60 76,52 68,68 60,52 44,58 50,42 35,32 50,28" fill="#2563eb" stroke="#000" strokeWidth="1.5" />
        <text x="65" y="42" textAnchor="middle" fill="#fff" fontSize="9" fontWeight="900" transform="rotate(-8 65 42)">DECODED!</text>

        {/* Public Forum Post Left */}
        <g transform="translate(25, 45)">
          <rect width="125" height="110" rx="6" fill="#1e293b" stroke="#64748b" strokeWidth="2" />
          <rect width="125" height="16" fill="#334155" rx="6" />
          <text x="8" y="11" fill="#94a3b8" fontSize="7">public-classifieds.com</text>
          <text x="10" y="32" fill="#fff" fontSize="8" fontWeight="bold">Vintage Watch for Sale</text>
          <rect x="15" y="40" width="95" height="50" rx="4" fill="#020617" />
          <circle cx="62" cy="65" r="18" fill="#334155" stroke="#f59e0b" strokeWidth="1.5" />
          <text x="10" y="102" fill="#94a3b8" fontSize="7">"Just a normal watch post..."</text>
        </g>

        {/* Magnifier Lens Center */}
        <g transform="translate(195, 45)">
          <circle cx="50" cy="45" r="35" fill="#10b981" fillOpacity="0.2" stroke="#34d399" strokeWidth="3" />
          <line x1="75" y1="70" x2="100" y2="95" stroke="#64748b" strokeWidth="7" strokeLinecap="round" />
          <line x1="50" y1="20" x2="50" y2="70" stroke="#34d399" strokeWidth="1" strokeDasharray="2 2" />
          <line x1="25" y1="45" x2="75" y2="45" stroke="#34d399" strokeWidth="1" strokeDasharray="2 2" />
          <text x="50" y="42" textAnchor="middle" fill="#a7f3d0" fontSize="8" fontFamily="monospace">GPS: 37°48'N</text>
          <text x="50" y="54" textAnchor="middle" fill="#a7f3d0" fontSize="8" fontFamily="monospace">122°24'W</text>
          <text x="50" y="118" textAnchor="middle" fill="#6ee7b7" fontSize="9" fontWeight="bold">CHI-SQUARE SCAN</text>
        </g>

        {/* Decoded Map Pin Right */}
        <g transform="translate(340, 45)">
          <rect width="130" height="110" rx="8" fill="#022c22" stroke="#10b981" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <text x="65" y="24" textAnchor="middle" fill="#a7f3d0" fontSize="9" fontWeight="bold">SECRET RENDEZVOUS</text>
          <path d="M 65 38 C 55 38 48 45 48 55 C 48 66 65 82 65 82 C 65 82 82 66 82 55 C 82 45 75 38 65 38 Z" fill="#ef4444" />
          <circle cx="65" cy="53" r="5" fill="#fff" />
          <text x="65" y="98" textAnchor="middle" fill="#fff" fontSize="8" fontFamily="monospace">Dock 42 @ 02:00 AM</text>
        </g>

        {/* Comic Dialogue Bottom */}
        <g transform="translate(20, 185)">
          <rect width="460" height="75" rx="6" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 2px 0px #000)" />
          <polygon points="120,0 135,-12 150,0" fill="#fff" stroke="#000" strokeWidth="2" />
          <rect x="121" y="0" width="28" height="4" fill="#fff" />
          <text x="16" y="24" fill="#1e3a8a" fontSize="12" fontWeight="900">ILLICIT COMMUNICATION CHANNEL EXPOSED</text>
          <text x="16" y="44" fill="#334155" fontSize="10.5">
            "Syndicate used public online classifieds as digital dead-drops. StegoVision AI flagged Chi-Square p-value equalization and extracted the secret rendezvous coordinates!"
          </text>
          <text x="16" y="62" fill="#059669" fontSize="10" fontWeight="bold">
            👉 CLICK IMAGE TO REVEAL HOW IT WORKS STEP-BY-STEP
          </text>
        </g>
      </svg>
    ),
    points: [
      {
        step: "Step 1: Dead-Drop 2.0",
        title: "Communication in Plain View",
        desc: "Criminal organizations avoid traceable chats by encoding secret directives into images uploaded to public classifieds, product catalogs, or forums.",
        icon: Terminal,
        color: "text-amber-600 bg-amber-50 border-amber-200",
      },
      {
        step: "Step 2: Chi-Square Fingerprint",
        title: "Statistical Proof of Equalized Pairs",
        desc: "StegoVision AI measures Chi-Square statistics over expanding pixel blocks. When LSB replacement equalizes color pairs, the p-value spikes to 1.0.",
        icon: Search,
        color: "text-sky-600 bg-sky-50 border-sky-200",
      },
      {
        step: "Step 3: Decoded Intelligence",
        title: "Actionable Law Enforcement Clues",
        desc: "The hidden rendezvous coordinates and passphrases are recovered and packaged into an evidence-grade audit report for prosecution.",
        icon: FileCheck,
        color: "text-emerald-700 bg-emerald-50 border-emerald-300",
      },
    ],
  },

  // --- COLUMN 2 (RIGHT SIDE) ---
  {
    id: "ransomware",
    col: "right",
    caseNumber: "CASE #04",
    actionBadge: "UNLOCKED!",
    actionColor: "bg-emerald-600 text-white",
    title: "The Ransomware Stash",
    tagline: "Recovering Decryption Keys in Cloud Avatars",
    badge: "Ransomware Defense",
    badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
    svg: (
      <svg viewBox="0 0 500 280" className="w-full h-auto select-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="c4bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#1e1b4b" />
            <stop offset="100%" stopColor="#064e3b" />
          </linearGradient>
        </defs>

        <rect width="500" height="280" fill="url(#c4bg)" />
        <rect x="6" y="6" width="488" height="268" fill="none" stroke="#000" strokeWidth="3" />

        {/* Action Burst */}
        <polygon points="50,15 70,22 85,12 82,30 98,35 84,45 92,60 76,52 68,68 60,52 44,58 50,42 35,32 50,28" fill="#10b981" stroke="#000" strokeWidth="1.5" />
        <text x="65" y="42" textAnchor="middle" fill="#fff" fontSize="9" fontWeight="900" transform="rotate(-8 65 42)">UNLOCKED!</text>

        {/* Locked Server Left */}
        <g transform="translate(25, 45)">
          <rect width="115" height="110" rx="6" fill="#18181b" stroke="#ef4444" strokeWidth="2" />
          <text x="57" y="24" textAnchor="middle" fill="#ef4444" fontSize="9" fontWeight="bold">SYSTEMS ENCRYPTED</text>
          <rect x="37" y="40" width="40" height="35" rx="4" fill="#dc2626" />
          <path d="M 45 40 L 45 28 Q 57 18 69 28 L 69 40" fill="none" stroke="#fca5a5" strokeWidth="4" />
          <text x="57" y="96" textAnchor="middle" fill="#f87171" fontSize="8">"Pay 5 BTC to recover"</text>
        </g>

        {/* Avatar Profile Center */}
        <g transform="translate(185, 35)">
          <rect width="125" height="130" rx="8" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <circle cx="62" cy="50" r="30" fill="#a78bfa" />
          <circle cx="62" cy="42" r="12" fill="#fff" />
          <path d="M 42 70 Q 62 55 82 70 Z" fill="#fff" />
          <text x="62" y="105" textAnchor="middle" fill="#0f172a" fontSize="10" fontWeight="bold">Cloud Profile Avatar</text>
          <text x="62" y="120" textAnchor="middle" fill="#4f46e5" fontSize="8">Keys Stashed in LSBs</text>
        </g>

        {/* Decryption Key Right */}
        <g transform="translate(340, 40)">
          <rect width="130" height="115" rx="8" fill="#064e3b" stroke="#34d399" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <circle cx="65" cy="50" r="22" fill="#022c22" stroke="#10b981" strokeWidth="2" />
          <path d="M 55 50 L 72 50 M 68 50 L 68 56 M 72 50 L 72 56" stroke="#fbbf24" strokeWidth="3" strokeLinecap="round" />
          <circle cx="55" cy="50" r="6" fill="none" stroke="#fbbf24" strokeWidth="3" />
          <text x="65" y="94" textAnchor="middle" fill="#6ee7b7" fontSize="10" fontWeight="bold">KEY EXTRACTED!</text>
          <text x="65" y="106" textAnchor="middle" fill="#a7f3d0" fontSize="8">Systems Decrypted Free</text>
        </g>

        {/* Comic Dialogue Bottom */}
        <g transform="translate(20, 185)">
          <rect width="460" height="75" rx="6" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 2px 0px #000)" />
          <polygon points="350,0 365,-12 380,0" fill="#fff" stroke="#000" strokeWidth="2" />
          <rect x="351" y="0" width="28" height="4" fill="#fff" />
          <text x="16" y="24" fill="#059669" fontSize="12" fontWeight="900">RANSOMWARE RESCUE: MASTER KEY RECOVERED</text>
          <text x="16" y="44" fill="#334155" fontSize="10.5">
            "Attackers hosted recovery keys inside benign profile avatars. StegoVision AI decoded the LSB channels, unlocking the victim company's files without paying any ransom!"
          </text>
          <text x="16" y="62" fill="#059669" fontSize="10" fontWeight="bold">
            👉 CLICK IMAGE TO REVEAL HOW IT WORKS STEP-BY-STEP
          </text>
        </g>
      </svg>
    ),
    points: [
      {
        step: "Step 1: Covert Key Escrow",
        title: "Hiding Decryption Keys in Avatars",
        desc: "Ransomware strains use steganography to store master encryption keys and infected machine victim lists in benign image banners and avatar pictures.",
        icon: Key,
        color: "text-amber-600 bg-amber-50 border-amber-200",
      },
      {
        step: "Step 2: Evading Outbound Alerts",
        title: "Traffic Looks Like Harmless CDN Browsing",
        desc: "Security operations centers monitor network traffic for suspicious C2 connections, but downloading an avatar image from a CDN raises zero alerts.",
        icon: Eye,
        color: "text-sky-600 bg-sky-50 border-sky-200",
      },
      {
        step: "Step 3: Incident Response Victory",
        title: "Immediate Key Extraction",
        desc: "StegoVision AI scans the avatar, isolates the embedded key bytes, and provides responders with the exact recovery key needed to restore servers.",
        icon: CheckCircle2,
        color: "text-emerald-700 bg-emerald-50 border-emerald-300",
      },
    ],
  },
  {
    id: "tamper",
    col: "right",
    caseNumber: "CASE #05",
    actionBadge: "EXPOSED!",
    actionColor: "bg-purple-600 text-white",
    title: "The Ghost in the Pixels",
    tagline: "Spotting Disinformation & Media Tampering",
    badge: "Media Verification",
    badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
    svg: (
      <svg viewBox="0 0 500 280" className="w-full h-auto select-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="c5bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#042f2e" />
            <stop offset="100%" stopColor="#0f172a" />
          </linearGradient>
        </defs>

        <rect width="500" height="280" fill="url(#c5bg)" />
        <rect x="6" y="6" width="488" height="268" fill="none" stroke="#000" strokeWidth="3" />

        {/* Action Burst */}
        <polygon points="50,15 70,22 85,12 82,30 98,35 84,45 92,60 76,52 68,68 60,52 44,58 50,42 35,32 50,28" fill="#9333ea" stroke="#000" strokeWidth="1.5" />
        <text x="65" y="42" textAnchor="middle" fill="#fff" fontSize="9" fontWeight="900" transform="rotate(-8 65 42)">EXPOSED!</text>

        {/* Viral Photo Left */}
        <g transform="translate(25, 45)">
          <rect width="115" height="110" rx="6" fill="#134e4a" stroke="#2dd4bf" strokeWidth="2" />
          <text x="57" y="22" textAnchor="middle" fill="#ccfbf1" fontSize="9" fontWeight="bold">VIRAL NEWS PHOTO</text>
          <rect x="10" y="30" width="95" height="65" rx="4" fill="#042f2e" />
          <circle cx="57" cy="55" r="16" fill="#fcd34d" />
          <path d="M 40 85 Q 57 70 74 85 Z" fill="#38bdf8" />
          <text x="57" y="104" textAnchor="middle" fill="#99f6e4" fontSize="7">"Looks completely natural"</text>
        </g>

        {/* LSB Diagnostic Map Center */}
        <g transform="translate(185, 35)">
          <rect width="125" height="130" rx="8" fill="#0f172a" stroke="#f59e0b" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <text x="62" y="22" textAnchor="middle" fill="#fde68a" fontSize="9" fontWeight="bold">LSB BIT-PLANE VIEW</text>
          <g transform="translate(12, 30)">
            <rect width="101" height="80" fill="#000" />
            <circle cx="20" cy="15" r="8" fill="#333" />
            <circle cx="55" cy="20" r="10" fill="#444" />
            {/* Tampered block */}
            <rect x="8" y="42" width="85" height="30" fill="#10b981" fillOpacity="0.3" stroke="#34d399" strokeWidth="1" strokeDasharray="2 2" />
            <text x="50" y="60" textAnchor="middle" fill="#a7f3d0" fontSize="7" fontFamily="monospace">ARTIFICIAL NOISE</text>
          </g>
          <text x="62" y="122" textAnchor="middle" fill="#fde68a" fontSize="7">Sensor vs Synthetic</text>
        </g>

        {/* Diagnostic Verdict Right */}
        <g transform="translate(340, 40)">
          <rect width="130" height="115" rx="8" fill="#022c22" stroke="#10b981" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <text x="65" y="24" textAnchor="middle" fill="#a7f3d0" fontSize="9" fontWeight="bold">FORENSIC VERDICT</text>
          <path d="M 35 75 A 30 30 0 0 1 95 75" fill="none" stroke="#334155" strokeWidth="7" strokeLinecap="round" />
          <path d="M 35 75 A 30 30 0 0 1 85 52" fill="none" stroke="#ef4444" strokeWidth="7" strokeLinecap="round" />
          <circle cx="65" cy="75" r="4" fill="#fff" />
          <text x="65" y="96" textAnchor="middle" fill="#ef4444" fontSize="11" fontWeight="900">TAMPERED</text>
          <text x="65" y="108" textAnchor="middle" fill="#a7f3d0" fontSize="8">RS Estimate: 82% Modified</text>
        </g>

        {/* Comic Dialogue Bottom */}
        <g transform="translate(20, 185)">
          <rect width="460" height="75" rx="6" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 2px 0px #000)" />
          <polygon points="210,0 225,-12 240,0" fill="#fff" stroke="#000" strokeWidth="2" />
          <rect x="211" y="0" width="28" height="4" fill="#fff" />
          <text x="16" y="24" fill="#9333ea" fontSize="12" fontWeight="900">INVISIBLE MANIPULATION BROUGHT TO LIGHT</text>
          <text x="16" y="44" fill="#334155" fontSize="10.5">
            "Human vision blends colors seamlessly. StegoVision AI maps the microscopic bitplane texture, separating organic camera noise from synthetic pixel injection!"
          </text>
          <text x="16" y="62" fill="#059669" fontSize="10" fontWeight="bold">
            👉 CLICK IMAGE TO REVEAL HOW IT WORKS STEP-BY-STEP
          </text>
        </g>
      </svg>
    ),
    points: [
      {
        step: "Step 1: The Invisible Edit",
        title: "Undetectable to Human Observers",
        desc: "Altering the least significant bit shifts color values by only 1 point (a 0.4% change), making synthetic modifications invisible to the naked eye.",
        icon: Eye,
        color: "text-amber-600 bg-amber-50 border-amber-200",
      },
      {
        step: "Step 2: Bit-Plane Diagnostics",
        title: "Visualizing Mathematical Texture",
        desc: "StegoVision renders an isolated bit-plane map. Natural cameras produce organic sensor gradients; manipulated regions show uniform artificial noise blocks.",
        icon: Search,
        color: "text-sky-600 bg-sky-50 border-sky-200",
      },
      {
        step: "Step 3: Quantitative Measurement",
        title: "RS Analysis & Channel Correlation",
        desc: "Regular-Singular group analysis measures the exact fraction of modified capacity without relying on black-box guesswork.",
        icon: CheckCircle2,
        color: "text-emerald-700 bg-emerald-50 border-emerald-300",
      },
    ],
  },
  {
    id: "copyright",
    col: "right",
    caseNumber: "CASE #06",
    actionBadge: "VERIFIED!",
    actionColor: "bg-emerald-600 text-white",
    title: "The Artist's Fingerprint",
    tagline: "Recovering Ownership Proof from Stolen Art",
    badge: "IP Protection",
    badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
    svg: (
      <svg viewBox="0 0 500 280" className="w-full h-auto select-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="c6bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#14532d" />
          </linearGradient>
        </defs>

        <rect width="500" height="280" fill="url(#c6bg)" />
        <rect x="6" y="6" width="488" height="268" fill="none" stroke="#000" strokeWidth="3" />

        {/* Action Burst */}
        <polygon points="50,15 70,22 85,12 82,30 98,35 84,45 92,60 76,52 68,68 60,52 44,58 50,42 35,32 50,28" fill="#10b981" stroke="#000" strokeWidth="1.5" />
        <text x="65" y="42" textAnchor="middle" fill="#fff" fontSize="8.5" fontWeight="900" transform="rotate(-8 65 42)">VERIFIED!</text>

        {/* Stolen Artwork Left */}
        <g transform="translate(25, 45)">
          <rect width="115" height="110" rx="6" fill="#1e293b" stroke="#e2e8f0" strokeWidth="2" />
          <text x="57" y="22" textAnchor="middle" fill="#f8fafc" fontSize="9" fontWeight="bold">STOLEN ARTWORK</text>
          <rect x="12" y="30" width="91" height="60" rx="4" fill="#334155" />
          <circle cx="45" cy="55" r="14" fill="#f59e0b" />
          <polygon points="30,85 55,60 85,85" fill="#10b981" />
          <text x="57" y="102" textAnchor="middle" fill="#ef4444" fontSize="7">"EXIF data was erased"</text>
        </g>

        {/* StegoVision Fingerprint Extractor Center */}
        <g transform="translate(185, 35)">
          <rect width="125" height="130" rx="8" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <circle cx="62" cy="48" r="28" fill="#ecfdf5" stroke="#10b981" strokeWidth="2" />
          <path d="M 52 48 Q 62 38 72 48 Q 62 58 52 48 Z" fill="none" stroke="#059669" strokeWidth="2" />
          <circle cx="62" cy="48" r="3" fill="#059669" />
          <text x="62" y="96" textAnchor="middle" fill="#0f172a" fontSize="9" fontWeight="bold">LSB Watermark</text>
          <text x="62" y="110" textAnchor="middle" fill="#059669" fontSize="8" fontFamily="monospace">Author: Elena Rostova</text>
          <text x="62" y="122" textAnchor="middle" fill="#64748b" fontSize="7">Hash Matched [✓]</text>
        </g>

        {/* Court Certificate Right */}
        <g transform="translate(340, 40)">
          <rect width="130" height="115" rx="8" fill="#022c22" stroke="#10b981" strokeWidth="2" filter="drop-shadow(2px 3px 0px #000)" />
          <text x="65" y="24" textAnchor="middle" fill="#a7f3d0" fontSize="9" fontWeight="bold">COURT-READY REPORT</text>
          <rect x="25" y="34" width="80" height="60" rx="2" fill="#fff" />
          <line x1="32" y1="44" x2="98" y2="44" stroke="#059669" strokeWidth="2" />
          <line x1="32" y1="52" x2="88" y2="52" stroke="#94a3b8" strokeWidth="1" />
          <line x1="32" y1="60" x2="92" y2="60" stroke="#94a3b8" strokeWidth="1" />
          <line x1="32" y1="68" x2="75" y2="68" stroke="#94a3b8" strokeWidth="1" />
          <circle cx="85" cy="78" r="6" fill="#10b981" />
          <text x="65" y="108" textAnchor="middle" fill="#6ee7b7" fontSize="8">PDF Audit Certificate</text>
        </g>

        {/* Comic Dialogue Bottom */}
        <g transform="translate(20, 185)">
          <rect width="460" height="75" rx="6" fill="#fff" stroke="#000" strokeWidth="2" filter="drop-shadow(2px 2px 0px #000)" />
          <polygon points="340,0 355,-12 370,0" fill="#fff" stroke="#000" strokeWidth="2" />
          <rect x="341" y="0" width="28" height="4" fill="#fff" />
          <text x="16" y="24" fill="#059669" fontSize="12" fontWeight="900">COPYRIGHT THEFT DEFEATED WITH RESILIENT PIXEL TAGS</text>
          <text x="16" y="44" fill="#334155" fontSize="10.5">
            "Art scrapers erased all metadata, but couldn't erase the microscopic LSB watermark. StegoVision AI recovered the artist's digital certificate and generated court evidence!"
          </text>
          <text x="16" y="62" fill="#059669" fontSize="10" fontWeight="bold">
            👉 CLICK IMAGE TO REVEAL HOW IT WORKS STEP-BY-STEP
          </text>
        </g>
      </svg>
    ),
    points: [
      {
        step: "Step 1: The Stripped Attribution",
        title: "Metadata Is Easily Removed",
        desc: "Image scrapers and content thieves easily wipe EXIF tags and IPTC headers to claim stolen photography and artwork as their own.",
        icon: Fingerprint,
        color: "text-amber-600 bg-amber-50 border-amber-200",
      },
      {
        step: "Step 2: Resilient Pixel Marking",
        title: "Watermarks Embedded Deep in Samples",
        desc: "Steganographic fingerprints embedded into the RGB pixels survive basic renaming, header stripping, and container format conversions.",
        icon: Search,
        color: "text-sky-600 bg-sky-50 border-sky-200",
      },
      {
        step: "Step 3: Legal Audit Trail",
        title: "Forensic Certificate of Authorship",
        desc: "StegoVision AI recovers the hidden artist ID and compiles a timestamped, tamper-evident PDF report establishing definitive ownership.",
        icon: FileBadge2,
        color: "text-emerald-700 bg-emerald-50 border-emerald-300",
      },
    ],
  },
];

export default function ComicExplainer({ onAnalyzeDemo }) {
  // Store the revealed count for each of the 6 comic panels (0 = none revealed, 1, 2, 3)
  const [revealed, setRevealed] = useState({
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
  });

  const handleImageClick = (idx) => {
    setRevealed((prev) => {
      const current = prev[idx] || 0;
      const total = COMIC_PANELS[idx].points.length;
      // Advance to next point one by one; cycle back to 1 if already complete
      const next = current < total ? current + 1 : 1;
      return { ...prev, [idx]: next };
    });
  };

  const handleReset = (idx, e) => {
    e.stopPropagation();
    setRevealed((prev) => ({ ...prev, [idx]: 0 }));
  };

  const handleRevealAll = () => {
    const full = {};
    COMIC_PANELS.forEach((_, i) => (full[i] = 3));
    setRevealed(full);
  };

  const handleHideAll = () => {
    const empty = {};
    COMIC_PANELS.forEach((_, i) => (empty[i] = 0));
    setRevealed(empty);
  };

  const leftPanels = COMIC_PANELS.map((p, i) => ({ ...p, originalIndex: i })).filter((p) => p.col === "left");
  const rightPanels = COMIC_PANELS.map((p, i) => ({ ...p, originalIndex: i })).filter((p) => p.col === "right");

  const renderComicCard = (comic) => {
    const idx = comic.originalIndex;
    const count = revealed[idx] || 0;
    const total = comic.points.length;
    const isComplete = count >= total;

    return (
      <div
        key={comic.id}
        className="card overflow-hidden border-2 border-slate-900 bg-white p-0 shadow-md hover:shadow-xl transition duration-300"
      >
        {/* Top Comic Book Header Strip */}
        <div className="flex items-center justify-between border-b-2 border-slate-900 bg-emerald-600 px-4 py-2.5 text-white">
          <div className="flex items-center gap-2">
            <span className="rounded bg-black px-2 py-0.5 font-mono text-[11px] font-extrabold tracking-wider text-emerald-300">
              {comic.caseNumber}
            </span>
            <span className="font-extrabold text-sm tracking-tight text-white">{comic.title}</span>
          </div>
          <span className="font-mono text-xs font-bold text-emerald-100">
            {count}/{total} CLUES
          </span>
        </div>

        {/* Comic Tagline */}
        <div className="bg-emerald-50/70 px-4 py-1.5 border-b border-emerald-900/10 flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-700">{comic.tagline}</span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${comic.badgeColor}`}>
            {comic.badge}
          </span>
        </div>

        {/* CLICKABLE COMIC IMAGE PANEL */}
        <div className="p-3 bg-slate-950/5">
          <div
            role="button"
            tabIndex={0}
            onClick={() => handleImageClick(idx)}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && handleImageClick(idx)}
            aria-label={`${comic.title} comic image. Click to reveal next clue under it.`}
            className="group relative cursor-pointer overflow-hidden rounded-lg border-2 border-slate-900 bg-slate-950 shadow-sm transition duration-200 hover:border-emerald-500 hover:shadow-md focus:outline-none focus:ring-4 focus:ring-emerald-500/40"
          >
            {/* The SVG Comic Art */}
            <div className="transition-transform duration-200 group-hover:scale-[1.01]">
              {comic.svg}
            </div>

            {/* Click Prompt Banner on the Image */}
            <div className="absolute bottom-2 right-2 z-10 flex items-center gap-1.5 rounded-full bg-slate-950/90 px-3 py-1 text-xs font-extrabold text-white shadow backdrop-blur border border-white/20 transition group-hover:bg-emerald-600">
              <MousePointerClick className="h-3.5 w-3.5 text-emerald-400 group-hover:text-white animate-pulse" />
              <span>
                {count === 0 && "CLICK TO REVEAL CLUES"}
                {count > 0 && count < total && `CLICK FOR POINT ${count + 1} OF ${total}`}
                {isComplete && "REVEALED! CLICK TO REPLAY"}
              </span>
            </div>

            {/* Status indicator top left */}
            <div className="absolute top-2 left-2 z-10 rounded bg-black/80 px-2 py-0.5 font-mono text-[11px] font-bold text-emerald-400 border border-emerald-500/40 backdrop-blur">
              {count === 0 ? "3 POINTS HIDDEN" : `${count} OF ${total} REVEALED`}
            </div>
          </div>
        </div>

        {/* POINTS REVEALED UNDER THE COMIC IMAGE */}
        <div className="p-4 bg-white border-t border-slate-200">
          <div className="mb-2.5 flex items-center justify-between">
            <span className="text-xs font-extrabold uppercase tracking-wider text-emerald-900">
              Forensic Points ({count}/{total}):
            </span>
            {count > 0 && (
              <button
                onClick={(e) => handleReset(idx, e)}
                className="text-[11px] font-semibold text-slate-500 hover:text-slate-800 flex items-center gap-1"
              >
                <RotateCcw className="h-2.5 w-2.5" /> Reset
              </button>
            )}
          </div>

          {/* If 0 points are revealed yet */}
          {count === 0 ? (
            <div
              onClick={() => handleImageClick(idx)}
              className="cursor-pointer rounded-lg border-2 border-dashed border-emerald-300 bg-emerald-50/40 p-4 text-center transition hover:bg-emerald-50/80"
            >
              <MousePointerClick className="mx-auto mb-1 h-5 w-5 text-emerald-600 animate-bounce" />
              <p className="text-xs font-bold text-slate-800">
                Click on the comic image above!
              </p>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Points will display under it one by one with each click.
              </p>
            </div>
          ) : (
            <div className="space-y-2.5">
              {/* Display revealed points one by one */}
              {comic.points.slice(0, count).map((pt, pIdx) => {
                const Icon = pt.icon;
                return (
                  <div
                    key={pt.step}
                    className="flex gap-2.5 rounded-lg border border-emerald-900/10 bg-emerald-50/40 p-3 shadow-xs animate-fade-up"
                    style={{ animationDuration: "0.25s" }}
                  >
                    <div className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md border ${pt.color}`}>
                      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-[10px] font-bold uppercase text-emerald-800">
                          {pt.step}
                        </span>
                        <span className="text-[10px] text-slate-400">Point {pIdx + 1}/3</span>
                      </div>
                      <h5 className="text-xs font-bold text-slate-900 mt-0.5">{pt.title}</h5>
                      <p className="text-[11px] text-slate-600 leading-snug mt-1">{pt.desc}</p>
                    </div>
                  </div>
                );
              })}

              {/* Next clue hint button */}
              {count < total && (
                <div
                  onClick={() => handleImageClick(idx)}
                  className="cursor-pointer rounded-md border border-dashed border-emerald-400/60 bg-emerald-50/30 py-1.5 text-center text-[11px] font-bold text-emerald-700 hover:bg-emerald-100/50 transition"
                >
                  👉 Click comic image above for Point {count + 1} of {total}…
                </div>
              )}

              {isComplete && (
                <div className="rounded-md bg-emerald-100/80 border border-emerald-300 py-1 text-center text-[11px] font-bold text-emerald-800">
                  ✓ Case Solved! All 3 points revealed.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <section className="mx-auto max-w-7xl px-4 sm:px-6 py-12">
      {/* Title & Headline */}
      <div className="text-center max-w-3xl mx-auto mb-8">
        <div className="inline-flex items-center gap-2 rounded-full border border-emerald-600/30 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800 shadow-xs mb-3">
          <Sparkles className="h-3.5 w-3.5 text-emerald-600" aria-hidden="true" /> 6 Real-World Comic Chronicles
        </div>
        <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          Real-Time Steganography Defense <span className="text-emerald-600">in Comics</span>
        </h2>
        <p className="mt-2 text-sm sm:text-base text-slate-600">
          6 real-time operational examples displayed across the sides of the page.
          <strong className="text-slate-900"> Click any comic image</strong> to unlock its forensic points one by one!
        </p>

        {/* Global Controls */}
        <div className="mt-4 flex flex-wrap justify-center gap-3">
          <button
            onClick={handleRevealAll}
            className="btn-ghost !py-1 !px-3 text-xs font-semibold text-emerald-800 border-emerald-300 bg-white shadow-xs"
          >
            Reveal All Points (All 6 Comics)
          </button>
          <button
            onClick={handleHideAll}
            className="btn-ghost !py-1 !px-3 text-xs font-semibold text-slate-600 border-slate-300 bg-white shadow-xs"
          >
            Reset All
          </button>
        </div>
      </div>

      {/* SIDES OF THE PAGE LAYOUT (2 Balanced Columns of 3 Comics Each) */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* LEFT SIDE COLUMN (Cases 1, 2, 3) */}
        <div className="space-y-6">
          <div className="border-b-2 border-emerald-600 pb-2 flex items-center justify-between">
            <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-600"></span>
              Left Side: Cyber Threat &amp; Intelligence Cases
            </h3>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">3 Cases</span>
          </div>
          {leftPanels.map((comic) => renderComicCard(comic))}
        </div>

        {/* RIGHT SIDE COLUMN (Cases 4, 5, 6) */}
        <div className="space-y-6">
          <div className="border-b-2 border-emerald-600 pb-2 flex items-center justify-between">
            <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-600"></span>
              Right Side: Ransomware &amp; Media Authentication Cases
            </h3>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">3 Cases</span>
          </div>
          {rightPanels.map((comic) => renderComicCard(comic))}
        </div>
      </div>
    </section>
  );
}
