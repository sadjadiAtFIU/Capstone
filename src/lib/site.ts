import { getCollection } from "astro:content";

export async function getSemesters() {
  const semesters = await getCollection("semesters");
  return semesters.sort((a, b) => {
    if (a.data.year !== b.data.year) {
      return b.data.year - a.data.year;
    }

    const order = { Spring: 1, Summer: 2, Fall: 3 };
    return (order[b.data.season as keyof typeof order] ?? 0) -
      (order[a.data.season as keyof typeof order] ?? 0);
  });
}
