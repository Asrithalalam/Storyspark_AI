import React from 'react';
import { Link } from 'react-router-dom';
import { PenLine, Image as ImageIcon, Sparkles, ArrowRight, Feather } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="w-full flex-1 flex flex-col items-center justify-start px-4 py-10 sm:px-6 md:py-14 text-center">
      <div className="w-full max-w-3xl space-y-12">
        {/* Short, Visual Hero */}
        <section className="space-y-4 max-w-xl mx-auto animate-in fade-in duration-300">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#E8DDD4] bg-[#FAF3EC] px-4 py-1 text-xs font-medium text-[#7D6B8D]">
            <Feather className="h-3.5 w-3.5 text-[#C85E45]" />
            <span className="font-serif font-semibold">StorySpark AI</span>
          </div>

          <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-[#2B1B2A] leading-tight">
            About StorySpark AI
          </h1>

          <p className="font-sans text-sm sm:text-base text-[#615060] leading-relaxed">
            A creative sanctuary where thoughts, dreams, and images become stories.
          </p>

          {/* Storytelling-Themed Decorative Art */}
          <div className="pt-2 flex justify-center">
            <div className="relative flex h-24 w-44 items-center justify-center">
              <svg
                className="w-32 h-32 text-[#C85E45]/80"
                viewBox="0 0 100 100"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.2"
              >
                <path d="M 15,70 Q 32,60 50,66 Q 68,60 85,70 L 85,32 Q 68,22 50,28 Q 32,22 15,32 Z" />
                <line x1="50" y1="28" x2="50" y2="66" />
                <circle cx="50" cy="18" r="2" fill="currentColor" />
                <path d="M 38,16 Q 50,12 62,16" strokeDasharray="1 1.5" />
              </svg>
            </div>
          </div>
        </section>

        {/* Three Visual Steps */}
        <section className="space-y-6">
          <div className="text-center space-y-1">
            <h2 className="font-serif text-xl sm:text-2xl font-bold text-[#2B1B2A]">
              Three Simple Steps
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-left">
            {/* Step 1 */}
            <div className="rounded-3xl border border-[#E8DFD5] bg-white p-6 shadow-2xs space-y-3 transition-transform hover:-translate-y-0.5">
              <div className="flex items-center justify-between">
                <div className="h-10 w-10 rounded-2xl bg-[#FAF0EB] flex items-center justify-center text-[#C85E45]">
                  <PenLine className="h-5 w-5" />
                </div>
                <span className="font-serif text-xs font-bold text-[#C85E45]/60">01</span>
              </div>
              <h3 className="font-serif text-base font-bold text-[#2B1B2A]">1. Written Idea</h3>
              <p className="font-sans text-xs font-normal text-[#6A5868] leading-relaxed">
                A thought, sentence, or memory to start your narrative journey.
              </p>
            </div>

            {/* Step 2 */}
            <div className="rounded-3xl border border-[#E8DFD5] bg-white p-6 shadow-2xs space-y-3 transition-transform hover:-translate-y-0.5">
              <div className="flex items-center justify-between">
                <div className="h-10 w-10 rounded-2xl bg-[#F4F0F7] flex items-center justify-center text-[#8E7C9D]">
                  <ImageIcon className="h-5 w-5" />
                </div>
                <span className="font-serif text-xs font-bold text-[#8E7C9D]/60">02</span>
              </div>
              <h3 className="font-serif text-base font-bold text-[#2B1B2A]">
                2. Image
              </h3>
              <p className="font-sans text-xs font-normal text-[#6A5868] leading-relaxed">
                Upload a photo or illustration to shape the setting and atmosphere.
              </p>
            </div>

            {/* Step 3 */}
            <div className="rounded-3xl border border-[#E8DFD5] bg-white p-6 shadow-2xs space-y-3 transition-transform hover:-translate-y-0.5">
              <div className="flex items-center justify-between">
                <div className="h-10 w-10 rounded-2xl bg-[#FAF0EB] flex items-center justify-center text-[#A24867]">
                  <Sparkles className="h-5 w-5" />
                </div>
                <span className="font-serif text-xs font-bold text-[#A24867]/60">03</span>
              </div>
              <h3 className="font-serif text-base font-bold text-[#2B1B2A]">
                3. Create Your Story
              </h3>
              <p className="font-sans text-xs font-normal text-[#6A5868] leading-relaxed">
                Choose genre and mood, then let imagination bring ideas to life.
              </p>
            </div>
          </div>
        </section>

        {/* Clear Call to Action */}
        <div className="pt-2">
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-[#C85E45] to-[#A24867] hover:from-[#B8523A] hover:to-[#913B57] px-7 py-3.5 text-xs sm:text-sm font-semibold text-white shadow-md shadow-[#C85E45]/20 transition-all cursor-pointer"
          >
            <span>Create a story</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};
