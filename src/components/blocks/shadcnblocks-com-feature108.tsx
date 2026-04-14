import { Tabs, TabsContent, TabsList, TabsTrigger } from "@radix-ui/react-tabs";
import { Layout, Pointer, Zap } from "lucide-react";

import { Button } from "@/components/ui/button";

interface TabContent {
  badge: string;
  title: string;
  description: string;
  buttonText: string;
  imageSrc: string;
  imageAlt: string;
}

interface Tab {
  value: string;
  icon: React.ReactNode;
  label: string;
  content: TabContent;
}

interface Feature108Props {
  badge?: string;
  heading?: string;
  description?: string;
  tabs?: Tab[];
}

const Feature108 = ({
  badge = "shadcnblocks.com",
  heading = "A Collection of Components Built With Shadcn & Tailwind",
  description = "Join us to build flawless web solutions.",
  tabs = [
    {
      value: "tab-1",
      icon: <Zap className="h-auto w-4 shrink-0" />,
      label: "Boost Revenue",
      content: {
        badge: "Modern Tactics",
        title: "Make your site a true standout.",
        description:
          "Discover new web trends that help you craft sleek, highly functional sites that drive traffic and convert leads into customers.",
        buttonText: "See Plans",
        imageSrc:
          "https://shadcnblocks.com/images/block/placeholder-dark-1.svg",
        imageAlt: "placeholder",
      },
    },
    {
      value: "tab-2",
      icon: <Pointer className="h-auto w-4 shrink-0" />,
      label: "Higher Engagement",
      content: {
        badge: "Expert Features",
        title: "Boost your site with top-tier design.",
        description:
          "Use stellar design to easily engage users and strengthen their loyalty. Create a seamless experience that keeps them coming back for more.",
        buttonText: "See Tools",
        imageSrc:
          "https://shadcnblocks.com/images/block/placeholder-dark-2.svg",
        imageAlt: "placeholder",
      },
    },
    {
      value: "tab-3",
      icon: <Layout className="h-auto w-4 shrink-0" />,
      label: "Stunning Layouts",
      content: {
        badge: "Elite Solutions",
        title: "Build an advanced web experience.",
        description:
          "Lift your brand with modern tech that grabs attention and drives action. Create a digital experience that stands out from the crowd.",
        buttonText: "See Options",
        imageSrc:
          "https://shadcnblocks.com/images/block/placeholder-dark-3.svg",
        imageAlt: "placeholder",
      },
    },
  ],
}: Feature108Props) => {
  return (
    <section className="bg-transparent py-14 text-[#2d3435] dark:text-[#f2f4f4] md:py-32">
      <div className="container mx-auto px-4 sm:px-6 md:px-8">
        <div className="mb-8 flex flex-col gap-6 md:mb-14 md:flex-row md:items-end md:justify-between lg:mb-16">
          <div className="flex flex-col gap-4">
            <h2 className="max-w-3xl text-3xl font-medium text-[#2d3435] dark:text-white md:text-4xl lg:text-5xl">
              {badge}
            </h2>
            <p className="text-xs uppercase tracking-[0.2em] text-[#745b3b] dark:text-[#b08b5a]">
              {heading}
            </p>
            <p className="max-w-lg text-[#848b8b] dark:text-[#a1a1aa]">{description}</p>
          </div>
        </div>
        <Tabs defaultValue={tabs[0].value}>
          <TabsList className="mb-8 flex items-center gap-5 overflow-x-auto whitespace-nowrap border-b border-black/10 pb-4 text-sm dark:border-white/10 md:flex-wrap md:gap-8">
            {tabs.map((tab) => (
              <TabsTrigger
                key={tab.value}
                value={tab.value}
                className="group flex items-center gap-2 pb-2 text-sm font-semibold text-[#848b8b] transition-colors dark:text-[#a1a1aa] data-[state=active]:text-[#2d3435] dark:data-[state=active]:text-white"
              >
                <span className="text-[#745b3b] opacity-60 transition-opacity group-data-[state=active]:opacity-100 dark:text-[#b08b5a]">
                  {tab.icon}
                </span>
                <span className="relative">
                  {tab.label}
                  <span className="absolute -bottom-6 left-0 h-px w-full scale-x-0 bg-[#745b3b] transition-transform group-data-[state=active]:scale-x-100 dark:bg-[#b08b5a]" />
                </span>
              </TabsTrigger>
            ))}
          </TabsList>
          <div className="mx-auto p-0 dark:border-white/10 dark:bg-[#121415] md:p-6 lg:p-16">
            {tabs.map((tab) => (
              <TabsContent
                key={tab.value}
                value={tab.value}
                className="grid place-items-center gap-8 lg:grid-cols-2 lg:gap-10"
              >
                <div className="flex flex-col gap-5">
                  <p className="text-xs uppercase tracking-[0.2em] text-[#745b3b] dark:text-[#b08b5a]">
                    {tab.content.badge}
                  </p>
                  <h3 className="text-3xl font-medium tracking-tight text-[#2d3435] dark:text-white lg:text-5xl">
                    {tab.content.title}
                  </h3>
                  <p className="max-w-lg text-[#848b8b] dark:text-[#a1a1aa] lg:text-lg">
                    {tab.content.description}
                  </p>
                  <Button className="mt-2.5 w-full gap-2 bg-[#2d3435] text-white hover:bg-[#1a1c1d] dark:bg-white dark:text-black dark:hover:bg-gray-200 sm:w-fit" size="lg">
                    {tab.content.buttonText}
                  </Button>
                </div>
                <img
                  src={tab.content.imageSrc}
                  alt={tab.content.imageAlt}
                  className="max-h-[280px] w-full object-contain dark:bg-[#0c0f0f] md:max-h-[400px]"
                />
              </TabsContent>
            ))}
          </div>
        </Tabs>
      </div>
    </section>
  );
};

export { Feature108 };
