export type SemesterProject = {
  id: string;
  title: string;
  slug: string;
  degreeProgram: string;
  shortDescription: string;
  teamMembers: string[];
  productOwners?: string[];
  posterUrl?: string;
  documentationUrl?: string;
  slidesUrl?: string;
  introVideoUrl?: string;
  demoVideoUrl?: string;
};

export type JudgeAssignment = {
  name: string;
  slots: {
    time: string;
    projectSlug: string;
    projectTitle: string;
    degreeProgram: string;
  }[];
};

export type StudentAssignment = {
  name: string;
  slots: {
    projectSlug: string;
    projectTitle: string;
    degreeProgram: string;
  }[];
};
