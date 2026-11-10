// Runs when Jenkins boots: create the "sdet-lab" pipeline job if it doesn't exist.
// The job reads the Jenkinsfile from the Git repo mounted at /project (branch main).
import hudson.plugins.git.BranchSpec
import hudson.plugins.git.GitSCM
import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob

def jenkins = Jenkins.get()
if (jenkins.getItem('sdet-lab') == null) {
    def scm = new GitSCM(
        GitSCM.createRepoList('file:///project', null),
        [new BranchSpec('*/main')],
        null, null, [])
    def job = jenkins.createProject(WorkflowJob, 'sdet-lab')
    job.definition = new CpsScmFlowDefinition(scm, 'Jenkinsfile')
    job.description = 'pytest API tests + headless Selenium UI tests for the radar console app'
    job.save()
    println 'Created job sdet-lab'
}
