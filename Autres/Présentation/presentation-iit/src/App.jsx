import React, { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, Layout, Palette, BarChart3, Zap, Users, Code, CheckCircle2, Monitor, Play } from 'lucide-react';

// images statiques importées via Vite
import djangoImg from './assets/interface_django.png';
import sidebarImg from './assets/sidebar.jpeg';
import dashboardImg from './assets/tableau_de_bord.jpeg';

const Slide = ({ children, active }) => (
  <div className={`absolute inset-0 transition-all duration-700 ease-in-out transform ${active ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}`}>
    <div className="h-full flex flex-col items-center justify-center p-8 text-center">
      {children}
    </div>
  </div>
);

const App = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    // Slide 1: Titre
    {
      content: (
        <div className="space-y-6">
          <div className="inline-block px-4 py-1 rounded-full bg-blue-100 text-blue-700 font-semibold text-sm mb-4">
            PROJET FIN DE CYCLE - L3 COMPUTER SCIENCE
          </div>
          <h1 className="text-6xl font-black text-slate-900 tracking-tight">
            IIT Admin <span className="text-blue-600">Custom</span>
          </h1>
          <p className="text-2xl text-slate-600 max-w-2xl mx-auto">
            Transformer l'administration Django standard en un tableau de bord professionnel de nouvelle génération.
          </p>
          <div className="pt-12 grid grid-cols-5 gap-4 text-sm font-medium text-slate-500">
            <span>Bléou Christ</span>
            <span>Sylla Scheickna</span>
            <span>Kouassi Nissi</span>
            <span>Kossonou Majo</span>
            <span>Yoboué Romuald</span>
          </div>
        </div>
      )
    },
    // Slide 2: Le Problème (Avec Image Django Standard)
    {
      content: (
        <div className="max-w-4xl w-full">
          <h2 className="text-4xl font-bold mb-12 text-slate-800 flex items-center justify-center gap-3 w-full">
            <Layout className="text-red-500" /> Le Constat : L'Admin Django Standard
          </h2>
          <div className="grid grid-cols-2 gap-8 items-center">
            <div className="bg-white p-2 rounded-2xl shadow-xl border border-slate-200 rotate-1 transform hover:rotate-0 transition-transform duration-500 min-h-[200px] flex flex-col items-center justify-center">
               <img 
                 src={djangoImg} 
                 alt="Interface Django" 
                 className="rounded-xl w-full h-auto object-cover"
                 onError={(e) => {
                   e.target.style.display = 'none';
                   e.target.nextSibling.style.display = 'block';
                 }} 
               />
               <div className="hidden text-slate-400 p-8 border-2 border-dashed border-slate-200 rounded-xl">
                 <Monitor className="mx-auto mb-2 opacity-20" size={48} />
                 <p className="text-xs italic">[Aperçu de l'interface Django Classique]</p>
               </div>
               <p className="mt-4 text-xs text-slate-400 italic font-medium">Capture d'écran de l'admin standard</p>
            </div>
            <ul className="text-left space-y-6 text-xl text-slate-700">
              <li className="flex items-start gap-3">
                <span className="bg-red-100 text-red-600 p-1 rounded font-bold">✕</span>
                Design daté et peu engageant
              </li>
              <li className="flex items-start gap-3">
                <span className="bg-red-100 text-red-600 p-1 rounded font-bold">✕</span>
                Absence de visualisation de données (KPIs)
              </li>
              <li className="flex items-start gap-3">
                <span className="bg-red-100 text-red-600 p-1 rounded font-bold">✕</span>
                Navigation rigide sur mobile
              </li>
            </ul>
          </div>
        </div>
      )
    },
    // Slide 3: Notre Solution
    {
      content: (
        <div className="space-y-8">
          <div className="h-16 w-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-blue-200">
            <Zap className="text-white w-10 h-10" />
          </div>
          <h2 className="text-5xl font-bold text-slate-900">La Révolution "Plug & Play"</h2>
          <p className="text-2xl text-slate-600 max-w-3xl">
            Un package réutilisable qui s'installe en <span className="text-blue-600 font-bold underline">30 secondes</span> et transforme radicalement l'expérience utilisateur.
          </p>
          <div className="grid grid-cols-3 gap-6 mt-12">
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
              <Palette className="w-12 h-12 text-purple-500 mb-4 mx-auto" />
              <h3 className="font-bold text-xl mb-2">7 Thèmes</h3>
              <p className="text-slate-500">Dark, Liquid Glass, Océan... Personnalisation totale.</p>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
              <BarChart3 className="w-12 h-12 text-emerald-500 mb-4 mx-auto" />
              <h3 className="font-bold text-xl mb-2">Analytics</h3>
              <p className="text-slate-500">Graphiques Chart.js dynamiques intégrés.</p>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
              <Zap className="w-12 h-12 text-orange-500 mb-4 mx-auto" />
              <h3 className="font-bold text-xl mb-2">Auto-Discovery</h3>
              <p className="text-slate-500">Détection intelligente de vos modèles.</p>
            </div>
          </div>
        </div>
      )
    },
    // Slide 4: Caractéristiques Techniques
    {
      content: (
        <div className="w-full max-w-5xl">
          <h2 className="text-4xl font-bold mb-12 text-slate-800">Sous le Capot</h2>
          <div className="grid grid-cols-2 gap-12 text-left">
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-slate-900 rounded-xl flex items-center justify-center text-white font-mono font-bold">Py</div>
                <div>
                  <h4 className="font-bold">Python / Django 5.0+</h4>
                  <p className="text-slate-500 text-sm">Architecture modulaire et robuste.</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center text-white">
                  <Monitor className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-bold">Bootstrap 5 & CSS Modern</h4>
                  <p className="text-slate-500 text-sm">Design responsive et animations fluides.</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-yellow-400 rounded-xl flex items-center justify-center text-white">
                  <BarChart3 className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-bold">Chart.js Engine</h4>
                  <p className="text-slate-500 text-sm">Moteur de rendu statistique automatique.</p>
                </div>
              </div>
            </div>
            <div className="bg-slate-900 rounded-2xl p-6 font-mono text-sm text-blue-400 overflow-hidden shadow-2xl">
              <div className="flex gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <p className="text-slate-500"># Installation simple</p>
              <p className="text-white">pip install personnalisation-admin-django-IIT</p>
              <p className="mt-4 text-slate-500"># Configuration settings.py</p>
              <p className="text-green-400">INSTALLED_APPS = [</p>
              <p className="pl-4 text-white">'admin_custom',</p>
              <p className="pl-4 text-white">'django.contrib.admin',</p>
              <p className="text-green-400">]</p>
            </div>
          </div>
        </div>
      )
    },
    // Slide 5: Focus Interface (Avec Sidebar et Dashboard)
    {
      content: (
        <div className="w-full">
          <h2 className="text-4xl font-bold mb-8 text-slate-800">Focus : L'Expérience Utilisateur</h2>
          <div className="grid grid-cols-2 gap-6 h-[400px]">
             <div className="bg-slate-800 rounded-2xl p-2 flex flex-col justify-end text-left text-white overflow-hidden relative group shadow-lg">
                <img 
                  src={sidebarImg} 
                  alt="Sidebar Custom" 
                  className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:scale-110 transition-transform duration-700"
                  onError={(e) => e.target.style.opacity = '0'}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent opacity-80"></div>
                <h4 className="relative font-bold z-10 text-xl px-4">Sidebar Rétractable</h4>
                <p className="relative text-xs text-slate-400 z-10 px-4 mb-4">Navigation optimisée avec FontAwesome 6.</p>
             </div>
             <div className="bg-blue-600 rounded-2xl p-2 flex flex-col justify-end text-left text-white overflow-hidden relative shadow-lg group">
                <img 
                  src={dashboardImg} 
                  alt="Tableau de Bord Custom" 
                  className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:scale-110 transition-transform duration-700"
                  onError={(e) => e.target.style.opacity = '0'}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-blue-900 via-transparent opacity-80"></div>
                <h4 className="relative font-bold z-10 text-xl px-4">Tableau de Bord</h4>
                <p className="relative text-xs text-blue-200 z-10 px-4 mb-4">Widgets statistiques personnalisables.</p>
             </div>
          </div>
          <p className="mt-8 text-slate-500 italic">"Conçu pour les administrateurs qui exigent clarté et rapidité."</p>
        </div>
      )
    },
    // Slide 6: L'Équipe
    {
      content: (
        <div className="w-full">
          <h2 className="text-4xl font-bold mb-12 text-slate-800 flex items-center justify-center gap-3">
            <Users className="text-blue-600" /> Le Groupe 4
          </h2>
          <div className="grid grid-cols-5 gap-6">
            {[
              { name: "Bléou Christ", role: "Scrum Master", icon: "🛡️" },
              { name: "Kouassi Nissi", role: "Product Owner", icon: "📋" },
              { name: "Sylla Scheickna", role: "Back-end Dev", icon: "⚙️" },
              { name: "Kossonou Majo", role: "QA Engineer", icon: "🔍" },
              { name: "Yoboué Romuald", role: "Front-end Dev", icon: "🎨" }
            ].map((member, i) => (
              <div key={i} className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-4xl mb-4 text-center">{member.icon}</div>
                <h4 className="font-bold text-slate-900 text-center">{member.name}</h4>
                <p className="text-sm text-blue-600 font-medium text-center">{member.role}</p>
              </div>
            ))}
          </div>
        </div>
      )
    },
    // Slide 7: Conclusion & Demo
    {
      content: (
        <div className="space-y-8">
          <CheckCircle2 className="w-20 h-20 text-green-500 mx-auto" />
          <h2 className="text-5xl font-bold text-slate-900">Projet à 95% Stable</h2>
          <p className="text-2xl text-slate-600 max-w-2xl mx-auto">
            Disponible dès maintenant pour les développeurs Django cherchant une interface premium sans effort.
          </p>
          <div className="flex gap-4 justify-center mt-12">
            <button className="bg-blue-600 text-white px-8 py-4 rounded-xl font-bold flex items-center gap-2 hover:bg-blue-700 transition-all transform hover:scale-105 active:scale-95 shadow-xl shadow-blue-200">
              <Play className="w-5 h-5" /> Place à la démo en direct !
            </button>
          </div>
          <p className="text-slate-400 pt-8 italic">Merci pour votre attention.</p>
        </div>
      )
    }
  ];

  const nextSlide = useCallback(() => setCurrentSlide((prev) => (prev + 1) % slides.length), [slides.length]);
  const prevSlide = useCallback(() => setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length), [slides.length]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowRight') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [nextSlide, prevSlide]);

  return (
    <div className="h-screen w-full bg-slate-50 flex flex-col font-sans overflow-hidden">
      {/* Barre de progression */}
      <div className="w-full h-1.5 bg-slate-200 flex">
        <div 
          className="h-full bg-blue-600 transition-all duration-300 ease-out"
          style={{ width: `${((currentSlide + 1) / slides.length) * 100}%` }}
        ></div>
      </div>

      <main className="flex-1 relative overflow-hidden">
        {slides.map((slide, index) => (
          <Slide key={index} active={currentSlide === index}>
            {slide.content}
          </Slide>
        ))}
      </main>

      {/* Contrôles de Navigation */}
      <div className="p-6 flex justify-between items-center bg-white border-t border-slate-200">
        <div className="flex items-center gap-2 text-slate-400 text-sm font-medium">
          <span className="text-slate-900 font-bold">{currentSlide + 1}</span> / {slides.length}
        </div>
        
        <div className="flex gap-4">
          <button 
            onClick={prevSlide}
            className={`p-3 rounded-full transition-colors border border-slate-200 ${currentSlide === 0 ? 'text-slate-200 cursor-not-allowed' : 'hover:bg-slate-100 text-slate-600'}`}
            disabled={currentSlide === 0}
            title="Précédent (Flèche gauche)"
          >
            <ChevronLeft />
          </button>
          <button 
            onClick={nextSlide}
            className="p-3 rounded-full bg-slate-900 text-white hover:bg-slate-800 transition-all shadow-lg active:scale-90"
            title="Suivant (Flèche droite)"
          >
            <ChevronRight />
          </button>
        </div>
      </div>
      
      {/* Logos & Branding */}
      <div className="absolute top-8 left-8 flex items-center gap-2 opacity-50 select-none pointer-events-none">
        <div className="bg-blue-600 text-white font-black px-2 py-0.5 rounded italic">IIT</div>
        <span className="font-bold tracking-widest text-xs uppercase">Groupe 4 | L3 CS</span>
      </div>
    </div>
  );
};

export default App;