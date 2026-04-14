"use client";

import { BadgePercent, Bell, CalendarDays } from "lucide-react";

import { Feature108 } from "@/components/blocks/shadcnblocks-com-feature108";

const demoData = {
  badge: "Announcements",
  heading: "A New Collection Built With Signature Style",
  description: "Keep up with announcements, new deals, and events from HMY.",
  tabs: [
    {
      value: "tab-1",
      icon: <Bell className="h-auto w-4 shrink-0" />,
      label: "Announcements",
      content: {
        badge: "Latest Note",
        title: "Fresh updates from the atelier.",
        description:
          "Catch the newest HMY notes, product highlights, and collection updates in one place.",
        buttonText: "Read Updates",
        imageSrc: "/annsoument.jpg",
        imageAlt: "Announcement board",
      },
    },
    {
      value: "tab-2",
      icon: <BadgePercent className="h-auto w-4 shrink-0" />,
      label: "New Deals",
      content: {
        badge: "Offer Highlight",
        title: "New pricing, selected with care.",
        description:
          "See the latest deals and bundle offers before the next refresh lands.",
        buttonText: "View Deals",
        imageSrc: "/deals.jpg",
        imageAlt: "New deal promotion",
      },
    },
    {
      value: "tab-3",
      icon: <CalendarDays className="h-auto w-4 shrink-0" />,
      label: "Events",
      content: {
        badge: "Upcoming Event",
        title: "Dates worth saving.",
        description:
          "Browse the events calendar for launches, gatherings, and seasonal moments.",
        buttonText: "See Events",
        imageSrc: "/event.jpg",
        imageAlt: "Event poster",
      },
    },
  ],
};

function Feature108Demo() {
  return (
    <div className="bg-white dark:bg-[#0c0f0f]">
      <Feature108 {...demoData} />
    </div>
  );
}

export { Feature108Demo };
