import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import logoHeader from "../assets/agri-ai-logo-header.png";
import { useAuth } from "../contexts/AuthContext";

const mainLinks = [
  { label: "Trang chủ", to: "/" },
  { label: "Tính năng", to: "/features" },
  { label: "Bài viết", to: "/articles" },
  { label: "Gói dịch vụ", to: "/pricing-plans" },
  { label: "Liên hệ", to: "/contact" },
];

const navClass = ({ isActive }) =>
  `rounded-2xl px-4 py-2 text-sm font-bold transition ${isActive
    ? "bg-emerald-100 text-emerald-800"
    : "text-slate-600 hover:bg-emerald-50 hover:text-emerald-700"
  }`;

export default function AgriNavbar() {
  const [open, setOpen] = useState(false);
  const { isAuthenticated } = useAuth();

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex min-h-20 items-center justify-between gap-4">
          <Link
            to="/"
            className="flex items-center gap-3 rounded-2xl focus:outline-none focus:ring-4 focus:ring-emerald-100"
            aria-label="Về trang chủ AgriAI"
          >
            <span className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl border border-emerald-100 bg-white shadow-sm">
              <img src={logoHeader} alt="AgriAI logo" className="h-full w-full object-cover object-center" />
            </span>
            <span className="leading-tight">
              <span className="block text-xl font-black tracking-tight text-slate-950">
                Agri<span className="text-emerald-600">AI</span>
              </span>
              <span className="hidden text-xs font-bold uppercase tracking-wide text-slate-500 sm:block">
                Nông nghiệp thông minh
              </span>
            </span>
          </Link>

          <nav className="hidden items-center gap-1 lg:flex" aria-label="Main navigation">
            {mainLinks.map((link) => (
              <NavLink key={link.to} to={link.to} className={navClass}>
                {link.label}
              </NavLink>
            ))}
          </nav>

          <div className="hidden items-center gap-2 lg:flex">
            <Link
              to="/ai-chat"
              className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-black text-emerald-700 transition hover:-translate-y-0.5 hover:bg-emerald-100"
            >
              Hỏi AI
            </Link>

            {!isAuthenticated && (
              <Link
                to="/login"
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-black text-slate-700 transition hover:-translate-y-0.5 hover:border-emerald-200 hover:text-emerald-700"
              >
                Đăng nhập
              </Link>
            )}

            {isAuthenticated && (
              <Link
                to="/dashboard"
                className="rounded-2xl bg-slate-950 px-4 py-2 text-sm font-black text-white shadow-lg shadow-slate-900/10 transition hover:-translate-y-0.5 hover:bg-emerald-700"
              >
                Vào hệ thống
              </Link>
            )}
          </div>

          <button
            type="button"
            onClick={() => setOpen((value) => !value)}
            className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-xl font-black text-slate-700 shadow-sm transition hover:bg-emerald-50 lg:hidden"
            aria-label="Mở menu"
            aria-expanded={open}
          >
            {open ? "×" : "☰"}
          </button>
        </div>

        {open && (
          <div className="border-t border-slate-100 py-4 lg:hidden">
            <nav className="grid gap-2" aria-label="Mobile navigation">
              {mainLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `rounded-2xl px-4 py-3 text-sm font-bold transition ${isActive
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-slate-50 text-slate-700 hover:bg-emerald-50 hover:text-emerald-700"
                    }`
                  }
                >
                  {link.label}
                </NavLink>
              ))}
            </nav>

            <div className="mt-4 grid gap-2 sm:grid-cols-3">
              <Link
                to="/ai-chat"
                onClick={() => setOpen(false)}
                className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-center text-sm font-black text-emerald-700"
              >
                Hỏi AI
              </Link>

              {!isAuthenticated && (
                <Link
                  to="/login"
                  onClick={() => setOpen(false)}
                  className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-center text-sm font-black text-slate-700"
                >
                  Đăng nhập
                </Link>
              )}

              {isAuthenticated && (
                <Link
                  to="/dashboard"
                  onClick={() => setOpen(false)}
                  className="rounded-2xl bg-slate-950 px-4 py-3 text-center text-sm font-black text-white"
                >
                  Vào hệ thống
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
